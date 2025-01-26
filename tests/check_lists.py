#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bot import TwitterBot
from src.logger import setup_logger

logger = setup_logger('list_checker')

def check_lists():
    """Check accessibility and content of both Twitter lists"""
    try:
        bot = TwitterBot()
        
        # Lists to check
        lists = {
            'current': '1872292999155040454',
            'new': '1882727258596450791'
        }
        
        for list_name, list_id in lists.items():
            print(f"\nChecking {list_name} list ({list_id})...")
            try:
                response = bot.client.get_list_tweets(
                    id=list_id,
                    max_results=5,
                    tweet_fields=['author_id', 'text']
                )
                
                if response and hasattr(response, 'data'):
                    print(f"✓ List accessible: Found {len(response.data)} recent tweets")
                    
                    # Show tweet previews
                    for tweet in response.data[:3]:
                        # Get author info
                        author = bot.client.get_user(id=tweet.author_id)
                        username = author.data.username if author and author.data else "unknown"
                        
                        preview = tweet.text[:100] + "..." if len(tweet.text) > 100 else tweet.text
                        print(f"\nTweet from @{username}:")
                        print(f"Content: {preview}")
                else:
                    print("✗ List appears empty or inaccessible")
                    
            except Exception as e:
                print(f"✗ Error accessing list: {str(e)}")
                
    except Exception as e:
        print(f"Error initializing bot: {str(e)}")
        return False
        
    return True

if __name__ == "__main__":
    check_lists()
