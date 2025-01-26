"""Crypto Twitter style and slang dictionary for enhancing GPT responses."""

import os
import random

# Common crypto terminology for natural conversation
CRYPTO_SLANG = {
    'greetings': ['hello', 'hi', 'hey', 'good morning'],
    'reactions': ['interesting', 'understood', 'noted'],
    'market': ['bullish', 'bearish', 'trending'],
    'technical': ['research', 'analysis', 'perspective']
}

def get_random_slang(category: str = None, probability: float = 0.15) -> str:
    """
    Get random slang element with specified probability
    Args:
        category: Optional category to select from
        probability: Chance of returning slang (0.0 to 1.0)
    Returns:
        str: Selected slang or empty string
    """
    if random.random() > probability:
        return ""
        
    if category and category in CRYPTO_SLANG:
        return random.choice(CRYPTO_SLANG[category])
    else:
        # Pick from technical or market categories for more professional tone
        professional_categories = ['technical', 'market']
        all_slang = []
        for category in professional_categories:
            if category in CRYPTO_SLANG:
                all_slang.extend(CRYPTO_SLANG[category])
        return random.choice(all_slang) if all_slang else ""

def enhance_response(response: str, tweet_text: str) -> str:
    """
    Enhance response with natural conversation style and appropriate terminology
    Args:
        response: Original GPT response
        tweet_text: Original tweet text for context
    Returns:
        str: Enhanced response with natural conversation style
    """
    tweet_lower = tweet_text.lower()
    
    # Calculate available space for enhancements
    available_chars = 280 - len(response)
    
    # Add natural greeting for morning tweets
    if available_chars > 5 and any(word in tweet_lower for word in ['gm', 'morning', 'hello', 'hi', '早上好']):
        prefix = get_random_slang('greetings', 0.3)
        if prefix and len(prefix) + 2 <= available_chars:
            response = f"{prefix}, {response}"
            available_chars -= len(prefix) + 2
    
    # Add relevant terminology for technical discussions
    if available_chars > 2 and any(word in tweet_lower for word in ['market', 'price', 'analysis', 'trend', 'bull', 'bear']):
        suffix = get_random_slang('technical', 0.2)
        if suffix and len(suffix) + 1 <= available_chars:
            response = f"{response}. From my {suffix}"
            available_chars -= len(suffix) + 1
    
    # Clean up response formatting
    response = response.replace('!', '.')  # Replace exclamation marks with periods
    response = ' '.join(word for word in response.split() if not word.startswith('#'))  # Remove hashtags
    
    # Remove any emojis (covering the full Unicode range for emojis)
    response = ''.join(c for c in response if not (
        '\U0001F300' <= c <= '\U0001F9FF' or  # Miscellaneous Symbols and Pictographs
        '\U0001F600' <= c <= '\U0001F64F' or  # Emoticons
        '\U0001F680' <= c <= '\U0001F6FF' or  # Transport and Map Symbols
        '\U0001F900' <= c <= '\U0001F9FF' or  # Supplemental Symbols and Pictographs
        '\U00002702' <= c <= '\U000027B0' or  # Dingbats
        '\U000024C2' <= c <= '\U0001F251'     # Enclosed characters
    ))
    
    # Add engagement prompts with 15% probability if there's space
    if random.random() < 0.15 and len(response) < 240:  # Leave room for the question
        questions = [
            "What are your thoughts on this?",
            "Have you experienced something similar?",
            "What's your take on this?",
            "How do you see it?",
            "What has been your experience?",
            "Do you agree with this perspective?",
            "How long have you been following this?",
            "What trends are you noticing?"
        ]
        question = random.choice(questions)
        response = f"{response} {question}"
    
    return response.strip()
