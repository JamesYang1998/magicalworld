"""
Twitter Analysis Tasks

This module defines Celery tasks for background processing of Twitter analysis.
"""
from celery import Celery
import os
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.kol_profile import KOLProfile
from app.services.twitter.bot_detection import analyze_followers
from app.services.twitter.content_analysis import analyze_content

# Initialize Celery
celery_app = Celery(
    "twitter_analysis",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
)

@celery_app.task
def analyze_followers_task(profile_id: int):
    """
    Background task to analyze followers of a Twitter account.
    
    Args:
        profile_id: ID of the KOL profile to analyze
    """
    # Get database session
    db = next(get_db())
    
    try:
        # Get profile
        profile = db.query(KOLProfile).filter(KOLProfile.id == profile_id).first()
        if not profile:
            print(f"Profile not found: {profile_id}")
            return
        
        # Analyze followers
        bot_percentage = analyze_followers(profile, db)
        
        print(f"Analyzed followers for profile {profile_id}: {bot_percentage}% bots")
    except Exception as e:
        print(f"Error analyzing followers: {str(e)}")
    finally:
        db.close()

@celery_app.task
def analyze_content_task(profile_id: int):
    """
    Background task to analyze content of a Twitter account.
    
    Args:
        profile_id: ID of the KOL profile to analyze
    """
    # Get database session
    db = next(get_db())
    
    try:
        # Get profile
        profile = db.query(KOLProfile).filter(KOLProfile.id == profile_id).first()
        if not profile:
            print(f"Profile not found: {profile_id}")
            return
        
        # Analyze content
        content_focus = analyze_content(profile, db)
        
        print(f"Analyzed content for profile {profile_id}: {content_focus}")
    except Exception as e:
        print(f"Error analyzing content: {str(e)}")
    finally:
        db.close()

@celery_app.task
def refresh_twitter_tokens_task():
    """
    Background task to refresh Twitter tokens that are about to expire.
    """
    # Get database session
    db = next(get_db())
    
    try:
        from datetime import datetime, timedelta
        from app.services.twitter.oauth import refresh_twitter_token
        
        # Get profiles with tokens that expire in the next hour
        expiry_threshold = datetime.now() + timedelta(hours=1)
        profiles = db.query(KOLProfile).filter(
            KOLProfile.twitter_token.isnot(None),
            KOLProfile.twitter_refresh_token.isnot(None),
            KOLProfile.twitter_token_expiry < expiry_threshold
        ).all()
        
        # Refresh tokens
        for profile in profiles:
            success = refresh_twitter_token(profile, db)
            print(f"Refreshed token for profile {profile.id}: {success}")
    except Exception as e:
        print(f"Error refreshing tokens: {str(e)}")
    finally:
        db.close()

# Schedule periodic tasks
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Refresh tokens every hour
    sender.add_periodic_task(
        3600,  # 1 hour
        refresh_twitter_tokens_task.s(),
        name='refresh-twitter-tokens'
    )
