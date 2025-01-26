#!/usr/bin/env python3

import os
import sys
from unittest.mock import Mock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.bot import TwitterBot  # noqa: E402
from src.llm import generate_response  # noqa: E402
from src.mock_data import MOCK_TWEETS, MOCK_USERS  # noqa: E402

def test_single_reply():
    """
    Test replying to a single tweet using GPT-3.5-turbo
    """
    try:
        print("Initializing Twitter bot...")
        bot = TwitterBot()
        
        # Use mock data for testing
        tweet_id = MOCK_TWEETS[0]['id']
        user_id = MOCK_TWEETS[0]['author_id']
        user_handle = MOCK_USERS[user_id]['username']
        original_tweet = MOCK_TWEETS[0]['text']
        
        print(f"\nPreparing to reply to tweet from @{user_handle}...")
        print(f"Original tweet: {original_tweet}")
        
        # Generate response using GPT-3.5-turbo
        print("\nGenerating reply content...")
        response_content = generate_response(original_tweet, model="gpt-3.5-turbo")
        print(f"Generated response: {response_content}")
        
        # Test reply functionality
        print("\nAttempting to post reply...")
        try:
            with patch.object(bot.client, 'create_tweet') as mock_create_tweet:
                mock_response = Mock()
                mock_response.data = {'id': '987654321'}
                mock_create_tweet.return_value = mock_response
                
                result = bot._reply_to_tweet(
                    tweet_id=tweet_id,
                    user_id=user_id,
                    user_handle=user_handle,
                    tweet_text=original_tweet
                )
                
                # Verify the reply was attempted with correct parameters
                mock_create_tweet.assert_called_once()
                call_args = mock_create_tweet.call_args[1]
                assert 'in_reply_to_tweet_id' in call_args, "Reply must include reference to original tweet"
                assert call_args['in_reply_to_tweet_id'] == tweet_id, "Reply must reference correct tweet ID"
                assert call_args['text'].startswith(f"@{user_handle}"), "Reply must mention original author"
                
                if result:
                    print("\nSuccess! Reply posted successfully!")
                    print(f"Original tweet ID: {tweet_id}")
                    print(f"Replied to: @{user_handle}")
                    return True
                else:
                    print("\nFailed to post reply")
                    return False
                
        except Exception as e:
            print(f"Error posting reply: {e}")
            return False
            
    except Exception as e:
        print(f"Error during test: {e}")
        return False

if __name__ == "__main__":
    test_single_reply()
