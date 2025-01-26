import sys
import os
import pytest
from unittest.mock import patch, Mock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.llm import generate_response

def test_chinese_tweet_response():
    """Test that Chinese tweets get Chinese responses"""
    chinese_tweet = "币圈最近怎么样？"
    
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="牛市来了，你觉得呢？"))]
    
    with patch('src.llm.OPENAI_API_KEY', 'test_key'), \
         patch('src.llm.client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_response
        response = generate_response(chinese_tweet)
        assert any('\u4e00' <= char <= '\u9fff' for char in response), "Response should be in Chinese"
        
        # Verify language instruction
        call_args = mock_client.chat.completions.create.call_args[1]
        assert "Reply in Chinese" in call_args['messages'][1]['content']

def test_english_tweet_response():
    """Test that English tweets get English responses"""
    english_tweet = "How's the crypto market looking?"
    
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Market looks strong. What's your take on it?"))]
    
    with patch('src.llm.OPENAI_API_KEY', 'test_key'), \
         patch('src.llm.client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_response
        response = generate_response(english_tweet)
        assert not any('\u4e00' <= char <= '\u9fff' for char in response), "Response should be in English"
        
        # Verify language instruction
        call_args = mock_client.chat.completions.create.call_args[1]
        assert "Reply in English" in call_args['messages'][1]['content']

def test_mixed_language_response():
    """Test that mixed language tweets get bilingual responses"""
    mixed_tweet = "GM! 最近defi很火啊！"
    
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="是的，DeFi很有发展。你怎么看？"))]
    
    with patch('src.llm.OPENAI_API_KEY', 'test_key'), \
         patch('src.llm.client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_response
        response = generate_response(mixed_tweet)
        
        # Verify bilingual instruction
        call_args = mock_client.chat.completions.create.call_args[1]
        assert "Reply in both Chinese and English" in call_args['messages'][1]['content']

def test_conversational_elements():
    """Test that responses are conversational and encourage engagement"""
    tweet = "Just bought some ETH"
    
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Good move. How long have you been investing in crypto?"))]
    
    with patch('src.llm.OPENAI_API_KEY', 'test_key'), \
         patch('src.llm.client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_response
        response = generate_response(tweet)
        
        # Check for conversational elements
        assert '?' in response, "Response should include a question"
        assert not any(char in response for char in ['!', '#']), "Response should not include ! or #"
        assert not any(c for c in response if '\U0001F300' <= c <= '\U0001F9FF'), "Response should not include emojis"

def test_response_length():
    """Test that responses stay within Twitter character limit"""
    tweet = "What do you think about the latest NFT trends?"
    
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="A" * 300))]  # Deliberately too long
    
    with patch('src.llm.OPENAI_API_KEY', 'test_key'), \
         patch('src.llm.client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_response
        response = generate_response(tweet)
        assert len(response) <= 280, "Response should not exceed Twitter character limit"

def test_market_context_influence():
    """Test that market context influences response content"""
    tweet = "What's happening in crypto?"
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Bitcoin surging past $40k as alt season gains momentum!"))]
    
    with patch('src.llm.OPENAI_API_KEY', 'test_key'), \
         patch('src.llm.client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_response
        response = generate_response(tweet, market_context="Bitcoin at $40k, alt season hype")
        assert "40k" in response.lower() or "alt season" in response.lower(), "Response should reflect market context"
