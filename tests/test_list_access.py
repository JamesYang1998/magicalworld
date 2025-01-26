import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.bot import TwitterBot  # noqa: E402


def test_list_access():
    bot = TwitterBot()
    list_id = "1872292999155040454"
    
    print(f"Testing access to list {list_id}...")
    try:
        response = bot.client.get_list_tweets(
            id=list_id,
            max_results=5,
            tweet_fields=['author_id', 'text']
        )
        if response and hasattr(response, 'data'):
            print(f"Successfully accessed list. Found {len(response.data)} recent tweets.")
            return True
        else:
            print("No tweets found in the list")
            return True  # Still consider it success if we can access the list
    except Exception as e:
        print(f"Failed to access list: {e}")
        return False

if __name__ == "__main__":
    test_list_access()
