"""Tests for dynamic presence penalty functionality."""

import sys
import os
from unittest.mock import patch, Mock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.llm import generate_response

def test_technical_tweet_presence_penalty():
    """Test that technical tweets get higher presence penalty."""
    technical_tweet = "What's your take on the latest DeFi yield farming protocols?"
    
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Test response"))]
    
    with patch('src.llm.OPENAI_API_KEY', 'test_key'), \
         patch('src.llm.client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_response
        generate_response(technical_tweet)
        
        # Verify presence_penalty was set to 0.7 for technical tweet
        call_args = mock_client.chat.completions.create.call_args[1]
        assert call_args['presence_penalty'] == 0.7

def test_casual_tweet_presence_penalty():
    """Test that casual tweets get lower presence penalty."""
    casual_tweet = "gm crypto fam! how's everyone doing today?"
    
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Test response"))]
    
    with patch('src.llm.OPENAI_API_KEY', 'test_key'), \
         patch('src.llm.client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_response
        generate_response(casual_tweet)
        
        # Verify presence_penalty was set to 0.6 for casual tweet
        call_args = mock_client.chat.completions.create.call_args[1]
        assert call_args['presence_penalty'] == 0.6

def test_mixed_content_tweet_presence_penalty():
    """Test that tweets with both casual and technical content get appropriate penalty."""
    mixed_tweet = "gm! excited about the new NFT marketplace launch!"
    
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Test response"))]
    
    with patch('src.llm.OPENAI_API_KEY', 'test_key'), \
         patch('src.llm.client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_response
        generate_response(mixed_tweet)
        
        # Should use higher penalty due to technical term "NFT"
        call_args = mock_client.chat.completions.create.call_args[1]
        assert call_args['presence_penalty'] == 0.7
