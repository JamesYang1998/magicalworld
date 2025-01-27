from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class AIProvider(str, Enum):
    OPENAI = "openai"
    DEEPSEEK = "deepseek"

class Message(BaseModel):
    role: str
    content: str

class Battle(BaseModel):
    """
    Represents an AI battle between OpenAI and DeepSeek models.
    
    Attributes:
        id: Unique identifier for the battle
        messages: List of messages exchanged during the battle
        winner: The winner of the battle (openai, deepseek, or tie)
        status: Current status of the battle (in_progress or completed)
        scores: Optional scores for each participant
    """
    id: str
    messages: List[Message]
    winner: Optional[str] = None
    status: str = "in_progress"
    scores: Optional[dict] = None

class BattleCreate(BaseModel):
    topic: str  # The topic or context for the battle
    rounds: int = 3  # Number of rounds in the battle

class Vote(BaseModel):
    """
    Represents a vote from a Twitter follower.
    
    Attributes:
        twitter_username: Twitter username of the voter
        chosen_ai: The AI provider they voted for (openai or deepseek)
    """
    twitter_username: str
    chosen_ai: str  # 'openai' or 'deepseek'

class BattleVotes(BaseModel):
    """
    Tracks votes for a battle.
    
    Attributes:
        battle_id: ID of the battle
        votes: List of votes cast
        vote_counts: Current vote counts for each AI
    """
    battle_id: str
    votes: List[Vote] = []
    vote_counts: dict = {"openai": 0, "deepseek": 0}
