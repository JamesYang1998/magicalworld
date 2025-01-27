import os
from typing import List, Optional
import uuid
import aiohttp
import logging
import tweepy
from .models import Message, Battle, AIProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    pass

class AIService:
    def __init__(self):
        # Load API keys from environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")
        
        # Validate API keys
        if not self.openai_api_key:
            logger.warning("OpenAI API key not configured")
        if not self.deepseek_api_key:
            logger.warning("DeepSeek API key not configured")
        
    async def get_ai_response(self, provider: AIProvider, messages: List[Message]) -> str:
        if provider == AIProvider.OPENAI:
            return await self._get_openai_response(messages)
        else:
            return await self._get_deepseek_response(messages)
    
    async def _get_openai_response(self, messages: List[Message]) -> str:
        if not self.openai_api_key:
            raise AIServiceError("OpenAI API key not configured")
            
        try:
            timeout = aiohttp.ClientTimeout(total=30)  # 30 seconds timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [m.dict() for m in messages],
                        "temperature": 0.9,
                        "max_tokens": 500  # Limit response length
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data["choices"][0]["message"]["content"]
                        logger.info(f"OpenAI response received: {response_text[:100]}...")
                        return response_text
                    else:
                        error_data = await response.text()
                        logger.error(f"OpenAI API error: {response.status} - {error_data}")
                        raise AIServiceError(f"OpenAI API error: {response.status} - {error_data}")
        except aiohttp.ClientError as e:
            logger.error(f"Network error calling OpenAI API: {str(e)}")
            raise AIServiceError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise AIServiceError(f"Failed to get OpenAI response: {str(e)}")

    async def _get_deepseek_response(self, messages: List[Message]) -> str:
        if not self.deepseek_api_key:
            raise AIServiceError("DeepSeek API key not configured")
            
        try:
            timeout = aiohttp.ClientTimeout(total=30)  # 30 seconds timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    "https://api.deepseek.com/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.deepseek_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [m.dict() for m in messages],
                        "temperature": 0.9,
                        "max_tokens": 500  # Limit response length
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data["choices"][0]["message"]["content"]
                        logger.info(f"DeepSeek response received: {response_text[:100]}...")
                        return response_text
                    else:
                        error_data = await response.text()
                        logger.error(f"DeepSeek API error: {response.status} - {error_data}")
                        raise AIServiceError(f"DeepSeek API error: {response.status} - {error_data}")
        except aiohttp.ClientError as e:
            logger.error(f"Network error calling DeepSeek API: {str(e)}")
            raise AIServiceError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Error calling DeepSeek API: {str(e)}")
            raise AIServiceError(f"Failed to get DeepSeek response: {str(e)}")

class TwitterService:
    def __init__(self):
        self.api_key = os.getenv("XAPI", "")
        if not self.api_key:
            logger.warning("Twitter API key not configured")
        
        # Initialize Twitter API client
        self.client = tweepy.Client(bearer_token=self.api_key)
        
    async def is_follower(self, username: str) -> bool:
        """Check if a user follows @jimsyoung_"""
        try:
            # Get the user ID for @jimsyoung_
            user = self.client.get_user(username="jimsyoung_")
            if not user.data:
                return False
                
            # Check if the given user follows @jimsyoung_
            follower = self.client.get_user(username=username)
            if not follower.data:
                return False
                
            # Check the following relationship
            follows = self.client.get_following(follower.data.id)
            return any(u.id == user.data.id for u in follows.data) if follows.data else False
            
        except Exception as e:
            logger.error(f"Error checking Twitter follower status: {str(e)}")
            return False

class BattleService:
    def __init__(self):
        self.ai_service = AIService()
        self.twitter_service = TwitterService()
        self.battles: dict[str, Battle] = {}
        self.battle_votes: dict[str, BattleVotes] = {}
        
    def create_battle(self, topic: str, rounds: int) -> Battle:
        battle_id = str(uuid.uuid4())
        initial_message = Message(
            role="system",
            content=f"You are participating in a verbal battle about: {topic}. Be competitive but respectful. Rounds: {rounds}"
        )
        battle = Battle(id=battle_id, messages=[initial_message])
        self.battles[battle_id] = battle
        return battle
        
    async def process_round(self, battle_id: str) -> Optional[Battle]:
        battle = self.battles.get(battle_id)
        if not battle:
            logger.warning(f"Battle {battle_id} not found")
            return None
            
        try:
            logger.info(f"Processing round for battle {battle_id}")
            
            # Get responses from both AIs
            openai_response = await self.ai_service.get_ai_response(
                AIProvider.OPENAI,
                battle.messages
            )
            battle.messages.append(Message(role="assistant", content=openai_response))
            logger.info(f"OpenAI response added to battle {battle_id}")
            
            deepseek_response = await self.ai_service.get_ai_response(
                AIProvider.DEEPSEEK,
                battle.messages
            )
            battle.messages.append(Message(role="assistant", content=deepseek_response))
            logger.info(f"DeepSeek response added to battle {battle_id}")
            
            # Update battle status and determine winner
            if len(battle.messages) >= 7:  # system + 3 rounds * 2 responses
                battle.status = "completed"
                
                # Initialize scores
                openai_score = 0
                deepseek_score = 0
                
                # Compare responses in pairs (each round)
                for i in range(1, len(battle.messages), 2):
                    openai_msg = battle.messages[i].content
                    deepseek_msg = battle.messages[i + 1].content if i + 1 < len(battle.messages) else ""
                    
                    # Score based on response length (basic metric)
                    openai_score += len(openai_msg.split())
                    deepseek_score += len(deepseek_msg.split())
                    
                    # Bonus points for coherent arguments (contains "because", "therefore", etc.)
                    reasoning_words = ["because", "therefore", "however", "moreover", "since", "thus"]
                    openai_score += sum(2 for word in reasoning_words if word.lower() in openai_msg.lower())
                    deepseek_score += sum(2 for word in reasoning_words if word.lower() in deepseek_msg.lower())
                
                # Store scores in battle object
                battle.scores = {
                    "openai": openai_score,
                    "deepseek": deepseek_score
                }
                
                # Determine winner
                if openai_score > deepseek_score:
                    battle.winner = "openai"
                elif deepseek_score > openai_score:
                    battle.winner = "deepseek"
                else:
                    battle.winner = "tie"
                
                logger.info(f"Battle {battle_id} completed. Winner: {battle.winner} (OpenAI: {openai_score}, DeepSeek: {deepseek_score})")
            
            return battle
            
        except AIServiceError as e:
            logger.error(f"Error processing round for battle {battle_id}: {str(e)}")
            raise
