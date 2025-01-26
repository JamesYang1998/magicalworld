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
    tweet = "How's the market looking today? Very bullish!"
    response = "Looking bullish!"
    
    # Test both slang and emoji addition for market discussion
    with patch('random.random', side_effect=[0.1, 0.05]), \
         patch('random.choice', side_effect=['alpha', '🚀']), \
         patch('os.getenv', return_value=None):
        enhanced = enhance_response(response, tweet)
        assert 'alpha' in enhanced  # Should include technical term
        assert '🚀' in enhanced  # Should include emoji for positive market context

def test_enhance_response_cleanup():
    """Test response cleanup (removing !, #, emojis)"""
    tweet = "Market is pumping! #bullrun 🚀"
    response = "Looking strong! #crypto"
    
    with patch('os.getenv', return_value=None):  # Not in test mode
        enhanced = enhance_response(response, tweet)
        assert '!' not in enhanced
        assert '#' not in enhanced
        assert '🚀' not in enhanced
        assert 'Looking strong' in enhanced

def test_enhance_response_character_limit():
    """Test that enhanced responses respect character limit"""
    tweet = "gm everyone"
    response = "x" * 275  # Near the limit
    
    enhanced = enhance_response(response, tweet)
    assert len(enhanced) <= 280  # Twitter's character limit

def test_enhance_response_engagement():
    """Test that responses can include engagement prompts"""
    tweet = "Just started learning about DeFi"
    response = "DeFi is transforming finance"
    
    with patch('random.random', return_value=0.1), \
         patch('random.choice', return_value="What has been your experience?"):
        enhanced = enhance_response(response, tweet)
        assert "?" in enhanced
        assert "What has been your experience?" in enhanced
        assert len(enhanced) <= 280
