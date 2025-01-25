import tweepy
from datetime import datetime, timedelta, timezone
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
from .llm import generate_response

class TwitterBot:
    def __init__(self):
        """Initialize Twitter bot with OAuth 1.0a client and tracking structures"""
        try:
            # Initialize Twitter API client with OAuth 1.0a
            self.client = tweepy.Client(
                bearer_token=os.getenv("BearerToken"),
                consumer_key=os.getenv("APIKey"),
                consumer_secret=os.getenv("APIKeySecret"),
                access_token=os.getenv("AccessToken"),
                access_token_secret=os.getenv("AccessTokenSecret")
            )
            # Initialize tracking structures
            self.daily_replies = {}  # Track daily replies per user
            self.max_daily_replies = 3
            self.processed_tweets = set()  # Track processed tweet IDs
            print("Twitter bot initialized successfully")
        except Exception as e:
            print(f"Error initializing Twitter bot: {e}")
            raise

    def monitor_list_tweets(self, list_id: str, interval: int = 60):
        """
        Monitor tweets from a Twitter list directly
        Args:
            list_id (str): ID of the Twitter list to monitor
            interval (int): Time between checks in seconds
        """
        print(f"Starting to monitor tweets from list {list_id} at {datetime.now(timezone.utc)}")
        
        try:
            while True:
                try:
                    print(f"\nChecking for new tweets at {datetime.now(timezone.utc)}")
                    response = self.client.get_list_tweets(
                        id=list_id,
                        max_results=10,
                        tweet_fields=['author_id', 'referenced_tweets', 'text']
                    )
                    
                    # Filter out retweets and replies
                    if response.data:
                        filtered_tweets = []
                        for tweet in response.data:
                            # Skip if it's a retweet or reply
                            if not (hasattr(tweet, 'referenced_tweets') and tweet.referenced_tweets):
                                filtered_tweets.append(tweet)
                        response.data = filtered_tweets
                    
                    if not response.data:
                        print("No new tweets found")
                        time.sleep(interval)
                        continue
                    
                    for tweet in response.data:
                        try:
                            tweet_id = str(tweet.id)
                            author_id = str(tweet.author_id)
                            
                            # Skip if we've already processed this tweet
                            if tweet_id in self.processed_tweets:
                                continue
                            
                            # Get author information
                            author = self.client.get_user(id=author_id)
                            if not hasattr(author, 'data') or not author.data:
                                print(f"Could not fetch author information for tweet {tweet_id}")
                                continue
                            
                            username = author.data.username
                            print(f"Processing tweet {tweet_id} from @{username}")
                        except AttributeError as e:
                            print(f"Error accessing tweet attributes: {e}")
                            continue
                        except Exception as e:
                            print(f"Unexpected error processing tweet: {e}")
                            continue
                        
                        # Check if we can reply to this user today
                        if self.can_reply_to_user(author_id):
                            print(f"New tweet from @{username}: {tweet.text[:50]}...")
                            if self._reply_to_tweet(tweet_id, author_id, username, tweet.text):
                                self.processed_tweets.add(tweet_id)
                        
                    # Prevent processed_tweets from growing too large
                    if len(self.processed_tweets) > 1000:
                        self.processed_tweets = set(list(self.processed_tweets)[-1000:])
                        
                    time.sleep(interval)
                    
                except tweepy.TooManyRequests as e:
                    reset_time = int(e.response.headers.get('x-rate-limit-reset', 900))
                    current_time = int(datetime.now(timezone.utc).timestamp())
                    sleep_time = max(reset_time - current_time, 60)
                    print(f"Rate limit exceeded. Waiting {sleep_time} seconds...")
                    time.sleep(sleep_time)
                    continue
                    
                except tweepy.TwitterServerError as e:
                    print(f"Twitter server error: {e}")
                    time.sleep(60)
                    continue
                    
                except Exception as e:
                    print(f"Error processing tweets: {e}")
                    time.sleep(30)
                    continue
                    
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
            return True
            
        return True

    def can_reply_to_user(self, user_id: str) -> bool:
        """
        Check if we can reply to a user based on daily limits
        """
        today = datetime.now().date()
        if user_id not in self.daily_replies:
            self.daily_replies[user_id] = {'date': today, 'count': 0}
        elif self.daily_replies[user_id]['date'] != today:
            self.daily_replies[user_id] = {'date': today, 'count': 0}
        
        return self.daily_replies[user_id]['count'] < self.max_daily_replies

    def monitor_tweets(self, list_id: str, interval: int = 60):
        """
        Deprecated: Use monitor_list_tweets instead
        This method is kept for backward compatibility
        """
        print("Warning: This method is deprecated. Please use monitor_list_tweets instead.")
        return self.monitor_list_tweets(list_id, interval)

    def _reply_to_tweet(self, tweet_id: str, user_id: str, user_handle: str, tweet_text: str):
        """
        Generate and post a reply to a tweet if within limits
        """
        if not self.can_reply_to_user(user_id):
            print(f"Daily reply limit reached for user {user_handle}")
            return False

        # Generate response using LLM
        response = generate_response(tweet_text)
        
        # Post reply
        try:
            self.client.create_tweet(
                text=f"@{user_handle} {response}",
                in_reply_to_tweet_id=tweet_id
            )
            self.daily_replies[user_id]['count'] += 1
            print(f"Successfully replied to @{user_handle}'s tweet: {tweet_text[:50]}...")
            return True
        except Exception as e:
            print(f"Error replying to tweet: {e}")
            return False
