from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.kol_profile import KOLProfile
from app.models.task import Task
from app.models.submission import TaskSubmission
from app.schemas.user import User as UserSchema
from app.schemas.kol_profile import KOLProfile as KOLProfileSchema
from app.schemas.task import Task as TaskSchema
from app.schemas.submission import Submission as SubmissionSchema
from app.services.auth import get_admin_user, get_current_active_user
from app.utils.excel_export import export_kol_data, export_tasks_data, export_submissions_data
from typing import List, Dict
from fastapi.responses import FileResponse

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=List[UserSchema])
async def get_all_users(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    users = db.query(User).all()
    return users

@router.get("/kol-profiles", response_model=List[KOLProfileSchema])
async def get_all_kol_profiles(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all KOL profiles (admin only)"""
    profiles = db.query(KOLProfile).all()
    return profiles

@router.get("/tasks", response_model=List[TaskSchema])
async def get_all_tasks(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all tasks (admin only)"""
    tasks = db.query(Task).all()
    return tasks

@router.get("/submissions", response_model=List[SubmissionSchema])
async def get_all_submissions(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all submissions (admin only)"""
    submissions = db.query(TaskSubmission).all()
    return submissions

@router.get("/export/kol-profiles")
async def export_kol_profiles(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Export KOL profiles to Excel (admin only)"""
    file_path = export_kol_data(db)
    return FileResponse(path=file_path, filename="kol_profiles.xlsx")

@router.get("/export/tasks")
async def export_tasks(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Export tasks to Excel (admin only)"""
    file_path = export_tasks_data(db)
    return FileResponse(path=file_path, filename="tasks.xlsx")

@router.get("/export/submissions")
async def export_submissions(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Export submissions to Excel (admin only)"""
    file_path = export_submissions_data(db)
    return FileResponse(path=file_path, filename="submissions.xlsx")

@router.post("/analyze-twitter/{profile_id}", response_model=Dict[str, bool])
async def analyze_twitter_profile(
    profile_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Trigger Twitter analysis for a KOL profile"""
    # Check if user is admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    # Get profile
    profile = db.query(KOLProfile).filter(KOLProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KOL profile not found",
        )
    
    # Schedule background tasks for analysis
    from app.tasks.twitter_analysis import analyze_followers_task, analyze_content_task
    analyze_followers_task.delay(profile.id)
    analyze_content_task.delay(profile.id)
    
    return {"success": True}
