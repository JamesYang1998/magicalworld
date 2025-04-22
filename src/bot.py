import os
import time
import logging
import json
from datetime import datetime, timedelta
import tweepy
from .llm import generate_response, STSIntegrator
from .logger import setup_logger

class TwitterBot:
    """Twitter bot that monitors a list and replies to tweets using GPT."""
    
    def __init__(self, sts_dir=None):
        """
        Initialize the Twitter bot.
        
        Args:
            sts_dir: Optional directory containing a Strategic Text Sequence
        """
        self.logger = setup_logger()
        self.logger.info("Initializing Twitter bot")
        
        self._setup_twitter_client()
        
        self.sts_integrator = None
        if sts_dir:
            self.sts_integrator = STSIntegrator(sts_dir)
            self.logger.info(f"STS integrator initialized with directory: {sts_dir}")
        
        self.daily_replies = {}
        self.reset_time = datetime.now() + timedelta(days=1)
        
        self.processed_tweets = set()
        
        self.monitored_users = {}
        
        self.max_daily_replies = 3
        
    def _setup_twitter_client(self):
        """Set up the Twitter API client using environment variables."""
        try:
            api_key = os.getenv('TWITTER_API_KEY')
            api_secret = os.getenv('TWITTER_API_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            
            if not all([api_key, api_secret, access_token, access_token_secret, bearer_token]):
                self.logger.error("Twitter API credentials not found in environment variables")
                raise ValueError("Missing Twitter API credentials")
            
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )
            
            self.logger.info("Twitter API client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting up Twitter API client: {str(e)}")
            raise
            
    def get_list_members(self, list_id):
        """
        Get members of a Twitter list.
        
        Args:
            list_id: ID of the Twitter list
            
        Returns:
            Dict mapping user IDs to usernames
        """
        try:
            self.logger.info(f"Getting members of list {list_id}")
            users = {}
            
            for user in tweepy.Paginator(
                self.client.get_list_members,
                list_id,
                max_results=100
            ):
                for member in user.data:
                    users[member.id] = member.username
                    
            self.logger.info(f"Found {len(users)} members in list {list_id}")
            return users
            
        except Exception as e:
            self.logger.error(f"Error getting list members: {str(e)}")
            return {}
            
    def _reset_daily_counters_if_needed(self):
        """Reset daily reply counters if the reset time has passed."""
        if datetime.now() >= self.reset_time:
            self.logger.info("Resetting daily reply counters")
            self.daily_replies = {}
            self.reset_time = datetime.now() + timedelta(days=1)
            
    def can_reply_to_user(self, user_id):
        """
        Check if a user can receive another reply based on daily limits.
        
        Args:
            user_id: ID of the Twitter user
            
        Returns:
            Boolean indicating whether the user can receive another reply
        """
        self._reset_daily_counters_if_needed()
        current_count = self.daily_replies.get(user_id, 0)
        return current_count < self.max_daily_replies
        
    def _reply_to_tweet(self, tweet_id, author_id, tweet_text):
        """
        Generate and post a reply to a tweet.
        
        Args:
            tweet_id: ID of the tweet to reply to
            author_id: ID of the tweet author
            tweet_text: Text of the tweet
            
        Returns:
            Boolean indicating whether the reply was successful
        """
        try:
            reply_text = generate_response(tweet_text, sts_integrator=self.sts_integrator)
            
            self.logger.info(f"Replying to tweet {tweet_id} by {self.monitored_users.get(author_id, author_id)}")
            self.client.create_tweet(
                text=reply_text,
                in_reply_to_tweet_id=tweet_id
            )
            
            self.daily_replies[author_id] = self.daily_replies.get(author_id, 0) + 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error replying to tweet {tweet_id}: {str(e)}")
            return False
            
    def monitor_list_tweets(self, list_id, interval=60):
        """
        Monitor tweets from members of a Twitter list and reply to them.
        
        Args:
            list_id: ID of the Twitter list to monitor
            interval: Polling interval in seconds
        """
        try:
            self.logger.info(f"Starting to monitor list {list_id} with interval {interval} seconds")
            
            self.monitored_users = self.get_list_members(list_id)
            
            if not self.monitored_users:
                self.logger.error(f"No members found in list {list_id}")
                return
                
            while True:
                try:
                    self._reset_daily_counters_if_needed()
                    
                    for user_id in self.monitored_users:
                        if not self.can_reply_to_user(user_id):
                            continue
                            
                        tweets = self.client.get_users_tweets(
                            user_id,
                            max_results=5,
                            exclude=['retweets', 'replies']
                        )
                        
                        if not tweets.data:
                            continue
                            
                        for tweet in tweets.data:
                            if tweet.id in self.processed_tweets:
                                continue
                                
                            self.processed_tweets.add(tweet.id)
                            
                            self._reply_to_tweet(tweet.id, user_id, tweet.text)
                            
                            break
                            
                    self.logger.info(f"Sleeping for {interval} seconds")
                    time.sleep(interval)
                    
                except Exception as e:
                    self.logger.error(f"Error during monitoring cycle: {str(e)}")
                    self.logger.info(f"Retrying in {interval} seconds")
                    time.sleep(interval)
                    
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Error monitoring list: {str(e)}")
