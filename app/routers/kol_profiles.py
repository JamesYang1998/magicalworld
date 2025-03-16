from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.kol_profile import KOLProfile
from app.schemas.kol_profile import KOLProfileCreate, KOLProfileUpdate, KOLProfile as KOLProfileSchema
from app.services.auth import get_current_active_user
from typing import List, Dict, Any

router = APIRouter(prefix="/kol-profiles", tags=["kol-profiles"])

@router.post("/", response_model=KOLProfileSchema)
async def create_kol_profile(
    profile: KOLProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if user is a KOL
    if current_user.role != UserRole.KOL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only KOLs can create profiles",
        )
    
    # Check if user already has a profile
    existing_profile = db.query(KOLProfile).filter(KOLProfile.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a KOL profile",
        )
    
    # Create new profile
    db_profile = KOLProfile(
        user_id=current_user.id,
        platform=profile.platform,
        platform_link=profile.platform_link,
        followers_count=profile.followers_count,
        content_focus=profile.content_focus,
        price_per_post=profile.price_per_post,
        wallet_address=profile.wallet_address
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@router.get("/me", response_model=KOLProfileSchema)
async def read_kol_profile_me(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if user is a KOL
    if current_user.role != UserRole.KOL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only KOLs can access profiles",
        )
    
    # Get user's profile
    profile = db.query(KOLProfile).filter(KOLProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KOL profile not found",
        )
    
    return profile

@router.put("/me", response_model=KOLProfileSchema)
async def update_kol_profile_me(
    profile_update: KOLProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if user is a KOL
    if current_user.role != UserRole.KOL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only KOLs can update profiles",
        )
    
    # Get user's profile
    profile = db.query(KOLProfile).filter(KOLProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KOL profile not found",
        )
    
    # Update profile fields
    if profile_update.platform is not None:
        profile.platform = profile_update.platform
    if profile_update.platform_link is not None:
        profile.platform_link = profile_update.platform_link
    if profile_update.followers_count is not None:
        profile.followers_count = profile_update.followers_count
    if profile_update.content_focus is not None:
        profile.content_focus = profile_update.content_focus
    if profile_update.price_per_post is not None:
        profile.price_per_post = profile_update.price_per_post
    if profile_update.wallet_address is not None:
        profile.wallet_address = profile_update.wallet_address
    
    db.commit()
    db.refresh(profile)
    return profile

@router.get("/{profile_id}", response_model=KOLProfileSchema)
async def read_kol_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    profile = db.query(KOLProfile).filter(KOLProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KOL profile not found",
        )
    
    return profile

@router.get("/{profile_id}/twitter-analysis", response_model=Dict[str, Any])
async def get_twitter_analysis(
    profile_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get Twitter analysis results for a KOL profile"""
    # Get profile
    profile = db.query(KOLProfile).filter(KOLProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KOL profile not found",
        )
    
    # Check if user is authorized
    if current_user.id != profile.user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    # Get bot percentage
    from app.services.twitter.bot_detection import get_bot_percentage
    bot_percentage = get_bot_percentage(profile, db)
    
    # Get content label
    from app.services.twitter.content_analysis import get_content_label
    content_label = get_content_label(profile, db)
    
    return {
        "bot_percentage": bot_percentage,
        "content_label": content_label,
        "bot_analysis_date": profile.bot_analysis_date,
        "content_analysis_date": profile.content_analysis_date,
        "twitter_verified": profile.twitter_verified
    }
