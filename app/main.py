from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from app.database import engine, Base
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.kol_profiles import router as kol_profiles_router
from app.routers.tasks import router as tasks_router
from app.routers.submissions import router as submissions_router
from app.routers.twitter import router as twitter_router
from app.routers.admin import router as admin_router
from app.tasks.twitter_analysis import celery_app

# Create FastAPI app
app = FastAPI(title="ACF Spark API", description="Backend API for ACF Spark KOL Platform")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(kol_profiles_router)
app.include_router(tasks_router)
app.include_router(submissions_router)
app.include_router(twitter_router)
app.include_router(admin_router)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    # Create exports directory
    os.makedirs("./exports", exist_ok=True)
    
    # Create database tables
    Base.metadata.create_all(bind=engine)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to ACF Spark API", "status": "online"}

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}
