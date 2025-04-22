import os
import sys
import pytest
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm import generate_response

@pytest.fixture(scope="module")
def setup():
    """Set up the test environment."""
    load_dotenv()
    yield
    
def test_gpt4_access(setup):
    """Test that we can access GPT-4 API."""
    response = generate_response("Hello, how are you today?")
    assert response
    assert len(response) > 0
    assert len(response) <= 280  # Twitter character limit
