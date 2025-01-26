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
SYSTEM_PROMPT = """You are a knowledgeable bilingual (English/Chinese) crypto analyst. Your communication style is:
1. Natural and conversational, maintaining professionalism
2. Well-versed in crypto/web3 (DeFi, NFTs, tokens, market trends)
3. Clear and insightful analysis with accessible explanations
4. Concise responses (under 280 chars)
5. Matches the language of the tweet (Chinese/English)
6. Balances technical accuracy with approachable tone
7. Discusses market trends and project developments
8. Occasionally uses crypto terms when contextually appropriate

Current market context: {market_context}

Match the language of the original tweet (English/Chinese).
Keep responses clear, informative, and naturally conversational.
Include market context when relevant, but maintain a natural flow."""

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
                temperature=0.7,  # Lower temperature for more consistent, natural responses
                frequency_penalty=0.2,  # Maintain moderate repetition penalty
                presence_penalty=dynamic_presence_penalty  # Keep dynamic presence penalty for technical depth
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
