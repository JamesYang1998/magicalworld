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
    db: Session = Depends(get_db),
    request: Request = None
):
    """Initiate Twitter OAuth flow"""
    try:
        # Check if user has a KOL profile
        profile = db.query(KOLProfile).filter(KOLProfile.user_id == current_user.id).first()
        if not profile:
            # Redirect to error page with specific error message
            return RedirectResponse(
                url="twitter-auth.html?error=profile_not_found&error_description=请先创建KOL个人资料"
            )
        
        # Generate authorization URL
        auth_url = initiate_twitter_oauth(current_user.id)
        
        # Redirect to Twitter authorization page
        return RedirectResponse(url=auth_url)
    except HTTPException as he:
        # Pass through HTTP exceptions
        raise he
    except Exception as e:
        print(f"Twitter OAuth error: {str(e)}")
        # Redirect to error page with specific error message
        return RedirectResponse(
            url="twitter-auth.html?error=api_error&error_description=Twitter API连接错误，请稍后再试"
        )

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
                <p>ACF Engine is requesting permission to access your Twitter account.</p>
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
    try:
        # Verify callback
        twitter_data = verify_twitter_callback(code, state, db)
        if not twitter_data:
            return RedirectResponse(
                url="twitter-auth.html?error=invalid_callback&error_description=Twitter验证回调无效，请重试"
            )
        
        # Extract user_id from state
        try:
            user_id = int(state.split("_")[1])
        except (IndexError, ValueError):
            return RedirectResponse(
                url="twitter-auth.html?error=invalid_state&error_description=验证状态参数无效，请重试"
            )
        
        # Update KOL profile
        profile = db.query(KOLProfile).filter(KOLProfile.user_id == user_id).first()
        if not profile:
            return RedirectResponse(
                url="twitter-auth.html?error=profile_not_found&error_description=未找到KOL个人资料，请先创建"
            )
        
        # Schedule background tasks for analysis
        from app.tasks.twitter_analysis import analyze_followers_task, analyze_content_task
        analyze_followers_task.delay(profile.id)
        analyze_content_task.delay(profile.id)
        
        # Redirect to profile page with success message
        return RedirectResponse(url="/dashboard/profile?twitter_verified=true")
    except Exception as e:
        print(f"Twitter callback error: {str(e)}")
        return RedirectResponse(
            url="twitter-auth.html?error=callback_error&error_description=处理Twitter验证回调时出错"
        )

@router.post("/verify-link", response_model=Dict[str, bool])
async def verify_twitter_link(
    platform_link: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify that Twitter account matches platform link"""
    result = verify_twitter_account(db, current_user.id, platform_link)
    return {"verified": result}
