import os
import sys
from unittest.mock import patch, Mock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.llm import generate_response  # noqa: E402

def test_generate_response_no_api_key():
    """Test response generation when API key is missing"""
    with patch('src.llm.OPENAI_API_KEY', None):
        response = generate_response("Test tweet")
        assert isinstance(response, str)
        assert "[Test Reply]" in response

def test_generate_response_success():
    """Test successful response generation"""
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Test response"))]
    
    with patch('src.llm.OPENAI_API_KEY', 'test_key'), \
         patch('src.llm.client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_response
        response = generate_response("Test tweet")
        assert response == "Test response"

def test_generate_response_long_text():
    """Test handling of responses exceeding character limit"""
    long_response = "x" * 300
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content=long_response))]
    
    with patch('src.llm.OPENAI_API_KEY', 'test_key'), \
         patch('src.llm.client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_response
        response = generate_response("Test tweet")
        assert len(response) <= 280
        assert response.endswith("...")

def test_generate_response_retry():
    """Test retry logic on API failure"""
    mock_success = Mock()
    mock_success.choices = [Mock(message=Mock(content="Success after retry"))]
    
    with patch('src.llm.OPENAI_API_KEY', 'test_key'), \
         patch('src.llm.client') as mock_client:
        mock_client.chat.completions.create.side_effect = [Exception("API Error"), mock_success]
        response = generate_response("Test tweet", max_retries=2)
        assert response == "Success after retry"

def test_generate_response_all_retries_failed():
    """Test handling when all retries fail"""
    with patch('src.llm.OPENAI_API_KEY', 'test_key'), \
         patch('src.llm.client') as mock_client:
        mock_client.chat.completions.create.side_effect = [Exception("API Error")] * 3
        response = generate_response("Test tweet", max_retries=2)
        assert "[Test Reply]" in response
