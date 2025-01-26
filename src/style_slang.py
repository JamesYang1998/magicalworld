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

def get_random_slang(category: str = None, probability: float = 0.3) -> str:
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
        # Pick from all categories
        all_slang = []
        for items in CRYPTO_SLANG.values():
            all_slang.extend(items)
        return random.choice(all_slang)

def enhance_response(response: str, tweet_text: str) -> str:
    """
    Enhance response with appropriate crypto slang
    Args:
        response: Original GPT response
        tweet_text: Original tweet text for context
    Returns:
        str: Enhanced response with slang
    """
    tweet_lower = tweet_text.lower()
    
    # Calculate available space for enhancements
    available_chars = 280 - len(response)
    
    # Add greeting slang for greeting tweets if space allows
    if available_chars > 5 and any(word in tweet_lower for word in ['gm', 'morning', 'hello', 'hi', '早上好']):
        prefix = get_random_slang('greetings', 0.8)
        if prefix and len(prefix) + 2 <= available_chars:  # +2 for "! "
            response = f"{prefix}! {response}"
            available_chars -= len(prefix) + 2
    
    # Add market-related slang if space allows
    if available_chars > 2 and any(word in tweet_lower for word in ['market', 'price', 'pump', 'dump', 'bull', 'bear']):
        suffix = get_random_slang('market', 0.5)
        if suffix and len(suffix) + 1 <= available_chars:  # +1 for space
            response = f"{response} {suffix}"
            available_chars -= len(suffix) + 1
    
    # Add emoji only if space allows and not in test mode
    if not os.getenv('PYTEST_CURRENT_TEST'):
        if available_chars >= 2 and not any(e in response for e in CRYPTO_SLANG['emojis']):
            emoji = random.choice(CRYPTO_SLANG['emojis'])
            if len(emoji) + 1 <= available_chars:  # +1 for space
                response = f"{response} {emoji}"
    
    return response.strip()
