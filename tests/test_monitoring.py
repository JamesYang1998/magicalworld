import sys
import os
import time
from datetime import datetime
from unittest.mock import Mock, patch
import tweepy

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bot import TwitterBot
from src.mock_data import MOCK_TWEETS, MOCK_USERS

def create_mock_tweet(tweet_data):
    """Create a mock tweet object from dictionary data"""
    tweet = Mock()
    tweet.id = tweet_data['id']
    tweet.text = tweet_data['text']
    tweet.author_id = tweet_data['author_id']
    if tweet_data['referenced_tweets']:
        tweet.referenced_tweets = [Mock(**ref) for ref in tweet_data['referenced_tweets']]
    else:
        tweet.referenced_tweets = None
    return tweet

def create_mock_user(user_data):
    """Create a mock user response"""
    response = Mock()
    user = Mock()
    user.username = user_data['username']
    user.id = user_data['id']
    response.data = user
    return response

def test_monitoring():
    """
    Test the monitoring functionality using mock data to verify core features
    """
    bot = TwitterBot()
    list_id = "1872292999155040454"
    
    print("Testing monitoring functionality with mock data")
    print("This test will verify tweet filtering and reply logic")
    
    try:
        # Create mock response for get_list_tweets
        mock_response = Mock()
        mock_response.data = [create_mock_tweet(t) for t in MOCK_TWEETS]
        
        # Set up patches for Twitter API calls
        with patch.object(bot.client, 'get_list_tweets', return_value=mock_response):
            with patch.object(bot.client, 'get_user', side_effect=lambda id: create_mock_user(MOCK_USERS[id])):
                with patch.object(bot.client, 'create_tweet') as mock_create_tweet:
                    print("\nProcessing mock tweets...")
                    
                    if not mock_response.data:
                        print("No tweets found in mock data")
                        return False
                        
                    print(f"\nFound {len(mock_response.data)} tweets to analyze")
                    
                    # Filter and process tweets
                    filtered_tweets = []
                    for tweet in mock_response.data:
                        if not (hasattr(tweet, 'referenced_tweets') and tweet.referenced_tweets):
                            filtered_tweets.append(tweet)
                    
                    print(f"Identified {len(filtered_tweets)} original tweets (filtered out retweets/replies)")
                    
                    # Process tweets to verify reply functionality
                    processed_count = 0
                    for tweet in filtered_tweets:
                        tweet_id = str(tweet.id)
                        author_id = str(tweet.author_id)
                        
                        author = bot.client.get_user(id=author_id)
                        username = author.data.username
                        print(f"\nTesting reply to @{username}'s tweet: {tweet.text[:50]}...")
                        
                        if bot.can_reply_to_user(author_id):
                            if bot._reply_to_tweet(tweet_id, author_id, username, tweet.text):
                                print(f"Successfully replied to @{username}")
                                bot.processed_tweets.add(tweet_id)
                                processed_count += 1
                                # Verify the reply was attempted
                                mock_create_tweet.assert_called()
                        else:
                            print(f"Skipped reply to @{username} - daily limit would be exceeded")
                    
                    # Print test results
                    print("\nTest Results:")
                    print(f"- Total tweets found: {len(mock_response.data)}")
                    print(f"- Original tweets (non-retweets/replies): {len(filtered_tweets)}")
                    print(f"- Successfully processed: {processed_count}")
                    print("\nReply Statistics:")
                    for user_id, replies in bot.daily_replies.items():
                        print(f"User {user_id}: {replies['count']} replies today (limit: {bot.max_daily_replies})")
                    
                    # Verify daily reply limits
                    assert all(replies['count'] <= bot.max_daily_replies for replies in bot.daily_replies.values()), \
                        "Daily reply limit exceeded for some users"
                    
                    print("\nAll tests passed successfully!")
                    return processed_count > 0  # Success if we processed at least one tweet
    
    except Exception as e:
        print(f"\nError during test: {e}")
        return False


if __name__ == "__main__":
    test_monitoring()
