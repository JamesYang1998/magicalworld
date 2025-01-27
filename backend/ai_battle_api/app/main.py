from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import os
from dotenv import load_dotenv

from .models import Battle, BattleCreate, Message, Vote, BattleVotes
from .services import BattleService, AIServiceError

description = """
🤖 AI Battle Arena API 🤖

This API enables AI battles between OpenAI and DeepSeek models. Watch them engage in verbal combat and see who emerges victorious!

## Battles

You can:
* Create new AI battles with specific topics
* Process battle rounds and watch the AIs debate
* Retrieve battle results and scores
"""

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Battle Arena",
    description=description,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)
battle_service = BattleService()

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/api/battles", response_model=Battle, tags=["battles"])
async def create_battle(battle_create: BattleCreate):
    """
    Create a new AI battle with a specific topic.
    
    - **topic**: The subject or context for the AI debate
    - **rounds**: Number of exchange rounds (default: 3)
    
    Returns the created battle object with a unique ID.
    """
    return battle_service.create_battle(
        topic=battle_create.topic,
        rounds=battle_create.rounds
    )

@app.post("/api/battles/{battle_id}/round", response_model=Battle, tags=["battles"])
async def process_battle_round(battle_id: str):
    """
    Process the next round of an ongoing battle.
    
    - Gets responses from both AI models
    - Updates battle state and scores
    - Determines winner if battle is complete
    
    Returns the updated battle object with new messages and scores.
    """
    try:
        battle = await battle_service.process_round(battle_id)
        if not battle:
            raise HTTPException(status_code=404, detail="Battle not found")
        return battle
    except AIServiceError as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/api/battles/{battle_id}", response_model=Battle, tags=["battles"])
async def get_battle(battle_id: str):
    """
    Get the current state of a battle.
    
    Returns:
    - Battle messages and progress
    - Current scores (if any)
    - Winner (if battle is completed)
    """
    battle = battle_service.battles.get(battle_id)
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    return battle

@app.post("/api/battles/{battle_id}/vote", response_model=BattleVotes, tags=["votes"])
async def vote_for_ai(battle_id: str, vote: Vote):
    """
    Cast a vote for an AI in a battle.
    
    Requirements:
    - Must be a Twitter follower of @jimsyoung_
    - Can only vote once per battle
    - Battle must be completed
    
    Returns the updated vote counts.
    """
    # Check if battle exists and is completed
    battle = battle_service.battles.get(battle_id)
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    if battle.status != "completed":
        raise HTTPException(status_code=400, detail="Cannot vote on an ongoing battle")
        
    # Verify Twitter follower status
    is_follower = await battle_service.twitter_service.is_follower(vote.twitter_username)
    if not is_follower:
        raise HTTPException(status_code=403, detail="Must be a follower of @jimsyoung_ to vote")
        
    # Initialize battle votes if not exists
    if battle_id not in battle_service.battle_votes:
        battle_service.battle_votes[battle_id] = BattleVotes(battle_id=battle_id)
        
    # Check if user already voted
    battle_votes = battle_service.battle_votes[battle_id]
    if any(v.twitter_username == vote.twitter_username for v in battle_votes.votes):
        raise HTTPException(status_code=400, detail="Already voted in this battle")
        
    # Add vote and update counts
    battle_votes.votes.append(vote)
    battle_votes.vote_counts[vote.chosen_ai] += 1
    
    # Update battle winner based on votes
    if battle_votes.vote_counts["openai"] > battle_votes.vote_counts["deepseek"]:
        battle.winner = "openai"
    elif battle_votes.vote_counts["deepseek"] > battle_votes.vote_counts["openai"]:
        battle.winner = "deepseek"
    # If tied, keep the original winner
    
    return battle_votes

@app.get("/api/battles/{battle_id}/votes", response_model=BattleVotes, tags=["votes"])
async def get_battle_votes(battle_id: str):
    """
    Get the current votes for a battle.
    
    Returns:
    - List of votes
    - Vote counts for each AI
    """
    if battle_id not in battle_service.battle_votes:
        return BattleVotes(battle_id=battle_id)
    return battle_service.battle_votes[battle_id]
