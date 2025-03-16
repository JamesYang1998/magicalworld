"""
Twitter API Client Module

This module provides a unified interface to the Twitter API with error handling,
rate limit management, and retry logic.
"""
import tweepy
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from sqlalchemy.orm import Session
from app.models.kol_profile import KOLProfile
from app.services.twitter.oauth import get_twitter_client, refresh_twitter_token

class TwitterClient:
    """Twitter API client with error handling and rate limit management."""
    
    def __init__(self, profile: KOLProfile, db: Session):
        """
        Initialize the Twitter client.
        
        Args:
            profile: KOL profile with Twitter tokens
            db: Database session
        """
        self.profile = profile
        self.db = db
        self.client = get_twitter_client(profile, db)
        self.max_retries = 3
    
    def _handle_rate_limit(self, response: Dict) -> bool:
        """
        Handle rate limit errors.
        
        Args:
            response: Twitter API response
            
        Returns:
            True if rate limited, False otherwise
        """
        if "errors" not in response:
            return False
        
        for error in response["errors"]:
            if error.get("code") == 88:  # Rate limit exceeded
                # Get rate limit reset time
                reset_time = error.get("reset", 0)
                if reset_time:
                    # Sleep until reset time
                    sleep_time = max(0, reset_time - time.time())
                    if sleep_time > 0 and sleep_time < 900:  # Max 15 minutes
                        time.sleep(sleep_time)
                        return True
                
                # Default sleep
                time.sleep(60)
                return True
        
        return False
    
    def _execute_with_retry(self, func: Callable, *args, **kwargs) -> Optional[Dict]:
        """
        Execute a Twitter API function with retry logic.
        
        Args:
            func: Twitter API function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            API response if successful, None otherwise
        """
        if not self.client:
            return None
        
        for attempt in range(self.max_retries):
            try:
                response = func(*args, **kwargs)
                
                # Check for rate limit
                if self._handle_rate_limit(response):
                    continue
                
                return response
            except tweepy.TweepyException as e:
                # Check for token expiration
                if "token" in str(e).lower() and "expired" in str(e).lower():
                    # Refresh token
                    if refresh_twitter_token(self.profile, self.db):
                        self.client = get_twitter_client(self.profile, self.db)
                        continue
                
                # Log the error
                print(f"Twitter API error (attempt {attempt+1}/{self.max_retries}): {str(e)}")
                
                # Sleep before retry
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def get_me(self, **kwargs) -> Optional[Dict]:
        """
        Get the authenticated user's information.
        
        Args:
            **kwargs: Additional parameters for the API call
            
        Returns:
            User data if successful, None otherwise
        """
        if not self.client:
            return None
        
        return self._execute_with_retry(self.client.get_me, **kwargs)
    
    def get_user_by_username(self, username: str, **kwargs) -> Optional[Dict]:
        """
        Get a user by username.
        
        Args:
            username: Twitter username
            **kwargs: Additional parameters for the API call
            
        Returns:
            User data if successful, None otherwise
        """
        if not self.client:
            return None
        
        return self._execute_with_retry(self.client.get_user, username=username, **kwargs)
    
    def get_followers(self, user_id: str, max_results: int = 100, **kwargs) -> Optional[List[Dict]]:
        """
        Get a user's followers.
        
        Args:
            user_id: Twitter user ID
            max_results: Maximum number of followers to return
            **kwargs: Additional parameters for the API call
            
        Returns:
            List of followers if successful, None otherwise
        """
        if not self.client:
            return None
        
        followers = []
        pagination_token = None
        
        while len(followers) < max_results:
            # Get a batch of followers
            response = self._execute_with_retry(
                self.client.get_users_followers,
                user_id,
                max_results=min(100, max_results - len(followers)),
                pagination_token=pagination_token,
                **kwargs
            )
            
            if not response or "data" not in response:
                break
            
            # Add followers to list
            batch = response["data"]
            if not batch:
                break
                
            followers.extend(batch)
            
            # Check if there are more followers
            meta = response.get("meta", {})
            pagination_token = meta.get("next_token")
            if not pagination_token:
                break
        
        return followers
    
    def get_tweets(self, user_id: str, max_results: int = 50, **kwargs) -> Optional[List[Dict]]:
        """
        Get a user's tweets.
        
        Args:
            user_id: Twitter user ID
            max_results: Maximum number of tweets to return
            **kwargs: Additional parameters for the API call
            
        Returns:
            List of tweets if successful, None otherwise
        """
        if not self.client:
            return None
        
        response = self._execute_with_retry(
            self.client.get_users_tweets,
            user_id,
            max_results=max_results,
            **kwargs
        )
        
        if not response or "data" not in response:
            return None
        
        return response["data"]
