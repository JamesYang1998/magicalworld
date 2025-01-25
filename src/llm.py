import time
from openai import OpenAI
from config.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_response(tweet_text: str, max_retries: int = 3, model: str = "gpt-3.5-turbo") -> str:
    """
    Generate a response to a tweet using OpenAI's GPT model
    Args:
        tweet_text: The text of the tweet to respond to
        max_retries: Maximum number of retries on API failure
    Returns:
        str: Generated response that fits Twitter's character limit
    """
    DEFAULT_RESPONSE = "[Test Reply] Thanks for sharing! This is a test response while monitoring functionality is being verified."
    TWITTER_CHAR_LIMIT = 280
    SYSTEM_PROMPT = """You are a friendly and engaging Twitter bot that generates thoughtful replies.
    Your responses should be:
    1. Concise and under 280 characters
    2. Relevant to the tweet's content
    3. Engaging but professional
    4. Free of hashtags or @mentions
    5. Natural and conversational
    Never include URLs or promotional content."""
    
    if not OPENAI_API_KEY:
        return DEFAULT_RESPONSE
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Generate a brief, engaging reply to this tweet (must be under {TWITTER_CHAR_LIMIT} characters): {tweet_text}"}
                ],
                max_tokens=100,
                temperature=0.7  # Slightly creative but still focused
            )
            
            reply = response.choices[0].message.content.strip()
            
            # Ensure response fits Twitter's character limit
            if len(reply) > TWITTER_CHAR_LIMIT:
                reply = reply[:TWITTER_CHAR_LIMIT-3] + "..."
            
            return reply
            
        except Exception as e:
            print(f"Error generating response (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:  # Last attempt failed
                return DEFAULT_RESPONSE
            time.sleep(2 ** attempt)  # Exponential backoff
    
    return DEFAULT_RESPONSE  # Ensure we always return a string
