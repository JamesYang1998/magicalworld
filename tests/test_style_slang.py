"""Tests for crypto style and slang functionality."""

import sys
import os
from unittest.mock import patch
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.style_slang import enhance_response, get_random_slang, CRYPTO_SLANG

def test_get_random_slang_categories():
    """Test getting slang from specific categories"""
    # Set random seed for reproducibility
    random.seed(42)
    
    # Test greeting category
    with patch('random.random', return_value=0.1):  # Ensure we get slang
        slang = get_random_slang('greetings')
        assert slang in CRYPTO_SLANG['greetings']
    
    # Test market category
    with patch('random.random', return_value=0.1):
        slang = get_random_slang('market')
        assert slang in CRYPTO_SLANG['market']

def test_get_random_slang_probability():
    """Test probability threshold for slang generation"""
    # Should not return slang
    with patch('random.random', return_value=0.9):
        assert get_random_slang(probability=0.3) == ""
    
    # Should return slang
    with patch('random.random', return_value=0.2):
        assert get_random_slang(probability=0.3) != ""

def test_enhance_response_greeting():
    """Test response enhancement for greeting tweets"""
    tweet = "gm crypto fam!"
    response = "Great day for crypto!"
    
    with patch('random.random', return_value=0.1), \
         patch('random.choice', return_value='wagmi'), \
         patch('os.getenv', return_value=None):  # Not in test mode
        enhanced = enhance_response(response, tweet)
        assert enhanced.startswith('wagmi!')
        assert 'Great day for crypto!' in enhanced

def test_enhance_response_market():
    """Test response enhancement for market discussion"""
    tweet = "How's the market looking today?"
    response = "Looking bullish!"
    
    with patch('random.random', return_value=0.1), \
         patch('random.choice', side_effect=['moon', '🚀']), \
         patch('os.getenv', return_value=None):  # Not in test mode
        enhanced = enhance_response(response, tweet)
        assert 'moon' in enhanced
        assert '🚀' in enhanced

def test_enhance_response_emoji():
    """Test that responses always include an emoji"""
    tweet = "Just a regular tweet"
    response = "Just a regular response"
    
    with patch('random.choice', return_value='🚀'), \
         patch('os.getenv', return_value=None):  # Not in test mode
        enhanced = enhance_response(response, tweet)
        assert '🚀' in enhanced

def test_enhance_response_character_limit():
    """Test that enhanced responses respect character limit"""
    tweet = "gm everyone!"
    response = "x" * 275  # Near the limit
    
    enhanced = enhance_response(response, tweet)
    assert len(enhanced) <= 280  # Twitter's character limit
