import os
import sys
import time
from datetime import datetime, timezone

import tweepy

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.llm import generate_response  # noqa: E402
from src.logger import setup_logger  # noqa: E402


logger = setup_logger('twitter_bot')


class TwitterBot:

    def __init__(self):
        """Initialize Twitter bot with OAuth 1.0a client and tracking structures"""
        try:
            # Initialize Twitter API client with OAuth 1.0a
            self.client = tweepy.Client(
                bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
                consumer_key=os.getenv("TWITTER_API_KEY"),
                consumer_secret=os.getenv("TWITTER_API_SECRET"),
                access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
            )
            # Initialize tracking structures
            self.daily_replies = {}  # Track daily replies per user
            self.max_daily_replies = 3
            self.processed_tweets = set()  # Track processed tweet IDs
            logger.info("Twitter bot initialized successfully")
        except Exception as e:
            logger.error("Error initializing Twitter bot", exc_info=True)
            raise


    def monitor_list_tweets(self, list_id: str, interval: int = 60, max_results: int = 5, single_pass: bool = False):
        """
        Monitor tweets from a Twitter list
        Args:
            list_id (str): ID of the Twitter list to monitor
            interval (int): Time between checks in seconds
            max_results (int): Maximum number of tweets to fetch per request (default: 5)
            single_pass (bool): If True, only check once and return; if False, monitor continuously
        Returns:
            bool: True if successful, False on error
        """
        logger.info(f"Starting to monitor tweets from list {list_id} at {datetime.now(timezone.utc)}")
        
        while True:
            try:
                logger.info(f"Checking list {list_id} for new tweets at {datetime.now(timezone.utc)}")
                response = self.client.get_list_tweets(
                    id=list_id,
                    max_results=max_results,
                    tweet_fields=['author_id', 'referenced_tweets', 'text']
                )
                
                # Filter out retweets and replies
                filtered_tweets = [
                    tweet for tweet in response.data
                    if not (hasattr(tweet, 'referenced_tweets') and tweet.referenced_tweets)
                ] if response.data else []
                
                if not filtered_tweets:
                    logger.info(f"No new tweets found in list {list_id}")
                    if single_pass:
                        return True
                    time.sleep(interval)
                    continue
                
                for tweet in filtered_tweets:
                    try:
                        tweet_id = str(tweet.id)
                        author_id = str(tweet.author_id)
                        
                        # Skip if we've already processed this tweet
                        if tweet_id in self.processed_tweets:
                            continue
                        
                        # Get author information
                        author = self.client.get_user(id=author_id)
                        if not hasattr(author, 'data') or not author.data:
                            logger.warning(f"Could not fetch author information for tweet {tweet_id}")
                            continue
                        
                        username = author.data.username
                        logger.info(f"Processing tweet {tweet_id} from @{username}")
                    except AttributeError as e:
                        logger.error(f"Error accessing tweet attributes: {e}", exc_info=True)
                        continue
                    except Exception as e:
                        logger.error(f"Unexpected error processing tweet: {e}", exc_info=True)
                        continue
                    
                    # Check if we can reply to this user today
                    if self.can_reply_to_user(author_id):
                        logger.info(f"New tweet from @{username}: {tweet.text[:50]}...")
                        if self._reply_to_tweet(tweet_id, author_id, username, tweet.text):
                            self.processed_tweets.add(tweet_id)
                    
                # Prevent processed_tweets from growing too large
                if len(self.processed_tweets) > 1000:
                    self.processed_tweets = set(list(self.processed_tweets)[-1000:])
                    
                if single_pass:
                    return True
                    
                time.sleep(interval)
                
            except tweepy.TooManyRequests as e:
                reset_time = int(e.response.headers.get('x-rate-limit-reset', 900))
                current_time = int(datetime.now(timezone.utc).timestamp())
                sleep_time = max(reset_time - current_time, 60)
                logger.warning(f"Rate limit exceeded for list {list_id}. Waiting {sleep_time} seconds...")
                time.sleep(sleep_time)
                if single_pass:
                    return False
                continue
                
            except tweepy.TwitterServerError as e:
                logger.error(f"Twitter server error for list {list_id}: {e}", exc_info=True)
                logger.info("Waiting 60 seconds before retry...")
                time.sleep(60)
                if single_pass:
                    return False
                continue
                
            except Exception as e:
                logger.error(f"Error processing tweets from list {list_id}: {e}", exc_info=True)
                logger.info("Waiting 30 seconds before retry...")
                time.sleep(30)
                if single_pass:
                    return False
                continue
                
        return True

    def monitor_multiple_lists(self, list_ids: list[str], interval: int = 90):
        """
        Monitor multiple Twitter lists sequentially
        Args:
            list_ids (list[str]): List of Twitter list IDs to monitor
            interval (int): Time between full cycles of checking all lists (default: 90s)
        Returns:
            bool: True if monitoring started successfully, False otherwise
        """
        if not list_ids:
            logger.error("No list IDs provided")
            return False
            
        logger.info(f"Starting to monitor {len(list_ids)} lists: {', '.join(list_ids)}")
        logger.info(f"Monitoring interval: {interval} seconds")
        
        # Calculate per-list parameters
        num_lists = len(list_ids)
        per_list_interval = 0  # No delay between lists
        per_list_max_results = max(5, min(10 // num_lists, 10))  # Adjust max_results based on list count
        
        try:
            while True:
                cycle_start = datetime.now(timezone.utc)
                logger.info(f"Starting new monitoring cycle at {cycle_start}")
                
                for list_id in list_ids:
                    self.monitor_list_tweets(
                        list_id,
                        interval=per_list_interval,
                        max_results=per_list_max_results,
                        single_pass=True
                    )
                
                # Calculate remaining time in the interval
                cycle_duration = (datetime.now(timezone.utc) - cycle_start).total_seconds()
                sleep_time = max(0, interval - cycle_duration)
                
                if sleep_time > 0:
                    logger.info(f"Cycle completed in {cycle_duration:.1f}s, sleeping for {sleep_time:.1f}s")
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
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
            logger.warning(f"Daily reply limit reached for user {user_handle}")
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
            preview = tweet_text[:47] + "..." if len(tweet_text) > 47 else tweet_text
            logger.info(f"Successfully replied to @{user_handle}'s tweet: {preview}")
            return True
        except Exception as e:
            logger.error("Error replying to tweet", exc_info=True)
            return False
