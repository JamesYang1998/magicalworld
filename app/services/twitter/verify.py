from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.kol_profile import KOLProfile
import os
import re
import json
from typing import Dict, Optional

# Mock Twitter API for development
# In production, this would use the Twitter API v2 OAuth 2.0 flow
class MockTwitterAPI:
    def __init__(self):
        self.auth_state = {}
        
    def generate_auth_url(self, user_id: int) -> str:
        """Generate a mock Twitter authorization URL"""
        state = f"user_{user_id}_{os.urandom(8).hex()}"
        self.auth_state[state] = user_id
        return f"/twitter/mock-auth?state={state}"
    
    def verify_callback(self, code: str, state: str) -> Optional[Dict]:
        """Verify the callback from Twitter"""
        if state not in self.auth_state:
            return None
        
        # Mock Twitter user data
        return {
            "id": "1234567890",
            "username": "kol_user123",
            "name": "KOL User",
            "followers_count": 5280,
            "verified": True,
            "profile_image_url": "https://pbs.twimg.com/profile_images/default_profile.png"
        }
    
    def extract_username_from_url(self, url: str) -> Optional[str]:
        """Extract Twitter username from profile URL"""
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

# Initialize mock Twitter API
twitter_api = MockTwitterAPI()

def initiate_twitter_oauth(user_id: int) -> str:
    """Initiate Twitter OAuth flow"""
    return twitter_api.generate_auth_url(user_id)

def verify_twitter_callback(code: str, state: str) -> Optional[Dict]:
    """Verify Twitter OAuth callback"""
    return twitter_api.verify_callback(code, state)

def verify_twitter_account(db: Session, user_id: int, platform_link: str) -> bool:
    """Verify that Twitter account matches platform link"""
    # Extract username from platform_link
    username = twitter_api.extract_username_from_url(platform_link)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Twitter profile URL",
        )
    
    # In a real implementation, we would verify with the Twitter API
    # For now, we'll just update the profile as verified
    profile = db.query(KOLProfile).filter(KOLProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KOL profile not found",
        )
    
    profile.twitter_verified = True
    db.commit()
    
    return True
