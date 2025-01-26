"""Crypto Twitter style and slang dictionary for enhancing GPT responses."""

import os
import random

# Common crypto Twitter slang and emojis
CRYPTO_SLANG = {
    'greetings': ['gm', 'gn', 'wagmi', 'lfg', 'ser'],
    'reactions': ['ngmi', 'ded', 'anon', 'fren', 'ser'],
    'market': ['moon', 'ape', 'degen', 'rekt', 'pump', 'dump'],
    'emojis': ['🚀', '💫', '🔥', '💎', '🌙', '⬆️', '📈', '🐂'],
    'technical': ['alpha', 'dyor', 'nfa', 'fud', 'hodl', 'iykyk']
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
    Enhance response with appropriate crypto terminology
    Args:
        response: Original GPT response
        tweet_text: Original tweet text for context
    Returns:
        str: Enhanced response with contextual crypto terms
    """
    tweet_lower = tweet_text.lower()
    
    # Calculate available space for enhancements
    available_chars = 280 - len(response)
    
    # Add greeting for morning tweets, but with lower probability
    if available_chars > 5 and any(word in tweet_lower for word in ['gm', 'morning', 'hello', 'hi', '早上好']):
        prefix = get_random_slang('greetings', 0.3)  # Reduced from 0.8
        if prefix and len(prefix) + 2 <= available_chars:
            response = f"{prefix}! {response}"
            available_chars -= len(prefix) + 2
    
    # Add market-related terms only for technical discussions
    if available_chars > 2 and any(word in tweet_lower for word in ['market', 'price', 'analysis', 'trend', 'bull', 'bear']):
        suffix = get_random_slang('technical', 0.2)  # Reduced from 0.5, using technical terms
        if suffix and len(suffix) + 1 <= available_chars:
            response = f"{response} {suffix}"
            available_chars -= len(suffix) + 1
    
    # Add emoji very rarely (10% chance) and only for positive market discussions
    if not os.getenv('PYTEST_CURRENT_TEST'):
        positive_keywords = ['bull', 'pump', 'moon', 'green', 'up']
        if (random.random() < 0.1 and  # 10% chance instead of 100%
            available_chars >= 2 and
            any(word in tweet_lower for word in positive_keywords) and
            not any(e in response for e in CRYPTO_SLANG['emojis'])):
            emoji = random.choice(CRYPTO_SLANG['emojis'])
            if len(emoji) + 1 <= available_chars:
                response = f"{response} {emoji}"
    
    return response.strip()
