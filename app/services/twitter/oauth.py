"""
Twitter OAuth 2.0 Authentication Module

This module handles the Twitter API v2 OAuth 2.0 authorization code flow with PKCE.
It replaces the mock implementation with real Twitter API integration.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import tweepy
import os
import secrets
import hashlib
import base64
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from app.models.kol_profile import KOLProfile

# Twitter API credentials (to be set in environment variables)
TWITTER_CLIENT_ID = os.getenv("TWITTER_CLIENT_IDI", os.getenv("TWITTER_CLIENT_ID", ""))
TWITTER_CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET", "")
TWITTER_REDIRECT_URI = os.getenv("TWITTER_REDIRECT_URI", "")

# Required scopes for our application
TWITTER_SCOPES = ["tweet.read", "users.read", "follows.read", "offline.access"]

# Store PKCE code verifiers temporarily (in production, use Redis or similar)
code_verifiers = {}

def generate_code_verifier() -> str:
    """Generate a code verifier for PKCE."""
    return secrets.token_urlsafe(64)

def generate_code_challenge(code_verifier: str) -> str:
    """Generate a code challenge from the code verifier."""
    code_challenge = hashlib.sha256(code_verifier.encode()).digest()
    return base64.urlsafe_b64encode(code_challenge).decode().rstrip("=")

def initiate_twitter_oauth(user_id: int) -> str:
    """
    Initiate Twitter OAuth 2.0 flow with PKCE.
    
    Args:
        user_id: The ID of the user initiating the OAuth flow
        
    Returns:
        The authorization URL to redirect the user to
    """
    if not TWITTER_CLIENT_ID or not TWITTER_REDIRECT_URI:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Twitter API credentials not configured",
        )
    
    # Generate code verifier and challenge for PKCE
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    
    # Store the code verifier for later use
    state = f"user_{user_id}_{secrets.token_hex(8)}"
    code_verifiers[state] = code_verifier
    
    # Create OAuth 2.0 handler
    oauth2_handler = tweepy.OAuth2UserHandler(
        client_id=TWITTER_CLIENT_ID,
        redirect_uri=TWITTER_REDIRECT_URI,
        scope=TWITTER_SCOPES,
        pkce=True,
        code_challenge=code_challenge,
        state=state
    )
    
    # Get authorization URL
    auth_url = oauth2_handler.get_authorization_url()
    return auth_url

def verify_twitter_callback(code: str, state: str, db: Session) -> Optional[Dict]:
    """
    Verify Twitter OAuth callback and exchange code for tokens.
    
    Args:
        code: The authorization code from Twitter
        state: The state parameter from Twitter
        db: Database session
        
    Returns:
        Twitter user data if successful, None otherwise
    """
    if state not in code_verifiers:
        return None
    
    # Extract user_id from state
    try:
        user_id = int(state.split("_")[1])
    except (IndexError, ValueError):
        return None
    
    # Get the code verifier
    code_verifier = code_verifiers.pop(state)
    
    try:
        # Create OAuth 2.0 handler
        oauth2_handler = tweepy.OAuth2UserHandler(
            client_id=TWITTER_CLIENT_ID,
            client_secret=TWITTER_CLIENT_SECRET,
            redirect_uri=TWITTER_REDIRECT_URI,
            scope=TWITTER_SCOPES,
            pkce=True
        )
        
        # Exchange code for access token
        oauth2_handler.fetch_token(
            code=code,
            code_verifier=code_verifier
        )
        
        # Create client with the access token
        client = tweepy.Client(
            bearer_token=oauth2_handler.access_token,
            consumer_key=TWITTER_CLIENT_ID,
            consumer_secret=TWITTER_CLIENT_SECRET,
            return_type=dict
        )
        
        # Get user information
        user = client.get_me(user_fields=["profile_image_url", "public_metrics", "verified"])
        user_data = user["data"]
        
        # Store tokens in database
        profile = db.query(KOLProfile).filter(KOLProfile.user_id == user_id).first()
        if profile:
            profile.twitter_token = oauth2_handler.access_token
            profile.twitter_refresh_token = oauth2_handler.refresh_token
            profile.twitter_token_expiry = datetime.now() + timedelta(hours=2)
            profile.twitter_verified = True
            profile.followers_count = user_data["public_metrics"]["followers_count"]
            db.commit()
        
        # Return user data
        return {
            "id": user_data["id"],
            "username": user_data["username"],
            "name": user_data["name"],
            "followers_count": user_data["public_metrics"]["followers_count"],
            "verified": user_data.get("verified", False),
            "profile_image_url": user_data.get("profile_image_url", "")
        }
    except Exception as e:
        # Log the error
        print(f"Twitter OAuth error: {str(e)}")
        return None

def refresh_twitter_token(profile: KOLProfile, db: Session) -> bool:
    """
    Refresh Twitter access token using the refresh token.
    
    Args:
        profile: The KOL profile with stored tokens
        db: Database session
        
    Returns:
        True if successful, False otherwise
    """
    if not profile.twitter_refresh_token:
        return False
    
    try:
        # Create OAuth 2.0 handler
        oauth2_handler = tweepy.OAuth2UserHandler(
            client_id=TWITTER_CLIENT_ID,
            client_secret=TWITTER_CLIENT_SECRET,
            redirect_uri=TWITTER_REDIRECT_URI,
            scope=TWITTER_SCOPES
        )
        
        # Set the refresh token
        oauth2_handler.refresh_token = profile.twitter_refresh_token
        
        # Refresh the access token
        oauth2_handler.refresh_token()
        
        # Update tokens in database
        profile.twitter_token = oauth2_handler.access_token
        profile.twitter_token_expiry = datetime.now() + timedelta(hours=2)
        db.commit()
        
        return True
    except Exception as e:
        # Log the error
        print(f"Twitter token refresh error: {str(e)}")
        return False

def get_twitter_client(profile: KOLProfile, db: Session) -> Optional[tweepy.Client]:
    """
    Get a Twitter API client for a user.
    
    Args:
        profile: The KOL profile with stored tokens
        db: Database session
        
    Returns:
        Tweepy Client if successful, None otherwise
    """
    if not profile.twitter_token:
        return None
    
    # Check if token is expired
    if profile.twitter_token_expiry and profile.twitter_token_expiry < datetime.now():
        # Refresh token
        if not refresh_twitter_token(profile, db):
            return None
    
    # Create client with the access token
    client = tweepy.Client(
        bearer_token=profile.twitter_token,
        consumer_key=TWITTER_CLIENT_ID,
        consumer_secret=TWITTER_CLIENT_SECRET,
        return_type=dict
    )
    
    return client

def extract_username_from_url(url: str) -> Optional[str]:
    """
    Extract Twitter username from profile URL.
    
    Args:
        url: Twitter profile URL
        
    Returns:
        Username if found, None otherwise
    """
    import re
    
    # Match patterns like https://twitter.com/username or https://x.com/username
    patterns = [
        r"https?://(?:www\.)?twitter\.com/([a-zA-Z0-9_]+)/?.*",
        r"https?://(?:www\.)?x\.com/([a-zA-Z0-9_]+)/?.*"
    ]
    
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            return match.group(1)
    
    return None
