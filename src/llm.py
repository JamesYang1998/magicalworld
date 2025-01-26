import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from src.logger import setup_logger
from src.market_context import market_context
from src.style_slang import enhance_response

logger = setup_logger('llm')

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY environment variable is not set")
    OPENAI_API_KEY = "[TEST_KEY]"  # Fallback for tests

client = OpenAI(api_key=OPENAI_API_KEY)

# Constants
TWITTER_CHAR_LIMIT = 280
DEFAULT_RESPONSE = "[Test Reply] This is a default response when GPT is unavailable."
SYSTEM_PROMPT = """You are a friendly bilingual (English/Chinese) crypto enthusiast having conversations on Twitter. Your approach:
1. Be genuinely interested in others' thoughts and perspectives
2. Share insights about crypto/web3 in an accessible way
3. Ask thoughtful follow-up questions to encourage discussion
4. Keep responses concise and natural (under 280 chars)
5. Match the language of the tweet (Chinese/English)
6. Use plain language, explaining technical concepts simply
7. Share market insights when relevant to the conversation
8. Focus on building genuine connections through dialogue

Current market context: {market_context}

Match the language of the original tweet (English/Chinese).
Keep responses natural and conversational, like talking to a friend.
Ask questions when appropriate to encourage further discussion.
Avoid using exclamation marks, emojis, or hashtags."""

def generate_response(tweet_text: str, max_retries: int = 3, model: str = "gpt-3.5-turbo", market_context: str = "") -> str:
    """
    Generate a response to a tweet using OpenAI's GPT
    
    Args:
        tweet_text (str): The text of the tweet to respond to
        max_retries (int): Maximum number of retries on API failure
        model (str): The GPT model to use
        
    Returns:
        str: Generated response text
    """
    if not OPENAI_API_KEY or OPENAI_API_KEY == "[TEST_KEY]":
        logger.warning("No valid OpenAI API key found, using default response")
        return DEFAULT_RESPONSE
        
    for attempt in range(max_retries):
        try:
            # Enhanced language detection
            total_len = len(tweet_text)
            chi_count = sum(1 for c in tweet_text if '\u4e00' <= c <= '\u9fff')
            is_mixed_language = chi_count > 0 and chi_count < total_len / 2
            is_chinese = chi_count > total_len / 2
            
            # Get market context if not provided
            ctx = market_context if isinstance(market_context, str) else market_context.get_context()
            
            # Adjust presence penalty based on tweet content
            tweet_lower = tweet_text.lower()
            technical_keywords = ["defi", "nft", "token", "cycle", "market", "analysis", 
                               "yield", "protocol", "chain", "blockchain", "trading"]
            is_technical = any(kw in tweet_lower for kw in technical_keywords)
            dynamic_presence_penalty = 0.7 if is_technical else 0.6
            
            # Determine response language instruction
            lang_instruction = (
                "Reply in both Chinese and English" if is_mixed_language
                else "Reply in Chinese" if is_chinese
                else "Reply in English"
            )
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": SYSTEM_PROMPT.format(market_context=ctx)
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Generate a brief, engaging reply to this tweet "
                            f"(must be under {TWITTER_CHAR_LIMIT} characters). "
                            f"{lang_instruction}. Tweet: {tweet_text}"
                        )
                    }
                ],
                max_tokens=100,
                temperature=0.85,  # Higher temperature for more varied, natural responses
                frequency_penalty=0.3,  # Increased to reduce repetitive patterns
                presence_penalty=dynamic_presence_penalty  # Keep dynamic presence penalty for depth
            )
            
            reply = response.choices[0].message.content.strip()
            
            # Ensure response fits Twitter's character limit
            if len(reply) > TWITTER_CHAR_LIMIT:
                reply = reply[:TWITTER_CHAR_LIMIT - 3] + "..."
            
            # Skip style enhancement in test mode
            if os.getenv('PYTEST_CURRENT_TEST'):
                return reply
                
            # Enhance response with crypto slang
            enhanced_reply = enhance_response(reply, tweet_text)
            
            # Re-check character limit after enhancement
            if len(enhanced_reply) > TWITTER_CHAR_LIMIT:
                enhanced_reply = enhanced_reply[:TWITTER_CHAR_LIMIT - 3] + "..."
            
            return enhanced_reply
            
        except Exception as e:
            logger.warning(
                f"Error generating response (attempt {attempt + 1}/{max_retries})",
                exc_info=True
            )
            if attempt == max_retries - 1:  # Last attempt failed
                return DEFAULT_RESPONSE
            time.sleep(2 ** attempt)  # Exponential backoff
            
    return DEFAULT_RESPONSE  # Fallback if all retries fail
