from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.kol_profile import KOLProfile
from app.services.auth import get_current_active_user
from app.services.twitter.oauth import initiate_twitter_oauth, verify_twitter_callback, extract_username_from_url
from app.services.twitter import verify_twitter_account
from typing import Dict

router = APIRouter(prefix="/twitter", tags=["twitter"])

@router.get("/authorize")
async def authorize_twitter(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Initiate Twitter OAuth flow"""
    # Check if user has a KOL profile
    profile = db.query(KOLProfile).filter(KOLProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KOL profile not found",
        )
    
    # Generate authorization URL
    auth_url = initiate_twitter_oauth(current_user.id)
    
    # Redirect to Twitter authorization page
    return RedirectResponse(url=auth_url)

@router.get("/mock-auth", response_class=HTMLResponse)
async def twitter_mock_auth(state: str):
    """Mock Twitter authorization page for development"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Twitter Authorization</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ccc; border-radius: 5px; }}
                .btn {{ background-color: #1DA1F2; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Twitter Authorization</h1>
                <p>ACF Spark is requesting permission to access your Twitter account.</p>
                <p>This will allow the platform to verify your account and access your follower count.</p>
                <button class="btn" onclick="window.location.href='/twitter/callback?code=mock_code&state={state}'">
                    Authorize
                </button>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get("/callback")
async def twitter_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle Twitter OAuth callback"""
    # Verify callback
    twitter_data = verify_twitter_callback(code, state, db)
    if not twitter_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid callback",
        )
    
    # Extract user_id from state
    try:
        user_id = int(state.split("_")[1])
    except (IndexError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter",
        )
    
    # Update KOL profile
    profile = db.query(KOLProfile).filter(KOLProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KOL profile not found",
        )
    
    # Schedule background tasks for analysis
    from app.tasks.twitter_analysis import analyze_followers_task, analyze_content_task
    analyze_followers_task.delay(profile.id)
    analyze_content_task.delay(profile.id)
    
    # Redirect to profile page
    return RedirectResponse(url="/dashboard/profile?twitter_verified=true")

@router.post("/verify-link", response_model=Dict[str, bool])
async def verify_twitter_link(
    platform_link: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify that Twitter account matches platform link"""
    result = verify_twitter_account(db, current_user.id, platform_link)
    return {"verified": result}
