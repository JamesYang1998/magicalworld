import os
import sys
import pytest
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bot import TwitterBot

@pytest.fixture(scope="module")
def setup():
    """Set up the test environment."""
    load_dotenv()
    yield
    
def test_twitter_api_connection(setup):
    """Test that we can connect to the Twitter API."""
    bot = TwitterBot()
    assert bot.client is not None
    
def test_list_members_retrieval(setup):
    """Test that we can retrieve members of a list."""
    test_list_id = "1234567890"
    
    if test_list_id == "1234567890":
        pytest.skip("No valid test list ID provided")
        
    bot = TwitterBot()
    members = bot.get_list_members(test_list_id)
    
    assert isinstance(members, dict)
    if members:
        assert all(isinstance(user_id, int) for user_id in members.keys())
        assert all(isinstance(username, str) for username in members.values())
