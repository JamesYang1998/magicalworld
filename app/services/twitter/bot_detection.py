"""
Twitter Bot Detection Module

This module analyzes Twitter followers to detect bot accounts and calculate
the percentage of bot followers for a KOL account.
"""
import tweepy
from datetime import datetime, timedelta
import re
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.kol_profile import KOLProfile
from app.services.twitter.oauth import get_twitter_client

def calculate_bot_score(follower: Dict) -> float:
    """
    Calculate a bot probability score for a Twitter follower.
    
    Args:
        follower: Twitter follower data
        
    Returns:
        Bot probability score (0-100)
    """
    score = 0
    max_score = 100
    
    # Account age (newer accounts more likely to be bots)
    created_at = datetime.strptime(follower.get("created_at", ""), "%Y-%m-%dT%H:%M:%S.%fZ")
    account_age_days = (datetime.now() - created_at).days
    if account_age_days < 30:
        score += 20
    elif account_age_days < 90:
        score += 10
    
    # Follower-to-following ratio (bots often follow many but have few followers)
    followers_count = follower.get("public_metrics", {}).get("followers_count", 0)
    following_count = follower.get("public_metrics", {}).get("following_count", 0)
    
    if followers_count > 0:
        ratio = following_count / followers_count
        if ratio > 50:
            score += 20
        elif ratio > 10:
            score += 10
    else:
        score += 15  # No followers is suspicious
    
    # Profile completeness
    if not follower.get("profile_image_url") or "default_profile" in follower.get("profile_image_url", ""):
        score += 15  # Default image is suspicious
    if not follower.get("description"):
        score += 10  # No bio is suspicious
    
    # Username patterns (random strings often indicate bots)
    if re.match(r'^[a-zA-Z0-9_]+\d{6,}$', follower.get("username", "")):
        score += 15  # Username with many trailing numbers
    
    # Tweet count (bots often have few tweets or excessive tweets)
    tweet_count = follower.get("public_metrics", {}).get("tweet_count", 0)
    if tweet_count < 10:
        score += 10  # Very few tweets is suspicious
    elif tweet_count > 100000:
        score += 10  # Excessive tweets can be suspicious
    
    # Verified accounts are unlikely to be bots
    if follower.get("verified", False):
        score -= 30
    
    # Normalize to 0-100%
    return min(100, max(0, score))

async def analyze_followers(profile: KOLProfile, db: Session) -> Optional[float]:
    """
    Analyze followers of a Twitter account to detect bots.
    
    Args:
        profile: KOL profile with Twitter tokens
        db: Database session
        
    Returns:
        Bot percentage if successful, None otherwise
    """
    # Get Twitter client
    client = get_twitter_client(profile, db)
    if not client:
        return None
    
    try:
        # Get user ID
        user = client.get_me()
        user_id = user["data"]["id"]
        
        # Get followers (paginated)
        followers = []
        pagination_token = None
        max_followers = 100  # Limit to 100 followers for analysis
        
        while len(followers) < max_followers:
            # Get a batch of followers
            response = client.get_users_followers(
                user_id,
                max_results=100,
                pagination_token=pagination_token,
                user_fields=["created_at", "description", "profile_image_url", "public_metrics", "verified"]
            )
            
            # Add followers to list
            batch = response.get("data", [])
            if not batch:
                break
                
            followers.extend(batch)
            
            # Check if there are more followers
            meta = response.get("meta", {})
            pagination_token = meta.get("next_token")
            if not pagination_token:
                break
        
        # Calculate bot scores
        if not followers:
            return None
            
        bot_scores = [calculate_bot_score(follower) for follower in followers]
        bot_percentage = sum(bot_scores) / len(bot_scores)
        
        # Update profile
        profile.bot_percentage = bot_percentage
        profile.bot_analysis_date = datetime.now()
        db.commit()
        
        return bot_percentage
    except Exception as e:
        # Log the error
        print(f"Follower analysis error: {str(e)}")
        return None

def get_bot_percentage(profile: KOLProfile, db: Session, force_refresh: bool = False) -> Optional[float]:
    """
    Get the bot percentage for a KOL profile.
    
    Args:
        profile: KOL profile
        db: Database session
        force_refresh: Whether to force a refresh of the analysis
        
    Returns:
        Bot percentage if available, None otherwise
    """
    # Check if we need to refresh the analysis
    if (force_refresh or 
        profile.bot_percentage is None or 
        profile.bot_analysis_date is None or 
        datetime.now() - profile.bot_analysis_date > timedelta(days=7)):
        # Schedule background task for analysis
        from app.tasks.twitter_analysis import analyze_followers_task
        analyze_followers_task.delay(profile.id)
        
    return profile.bot_percentage
