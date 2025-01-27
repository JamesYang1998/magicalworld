import tweepy
import openai
import asyncio
import os
import logging
import time
from typing import Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TwitterTranslator:
    def __init__(self, bearer_token: str, api_key: str, api_secret: str, 
                 access_token: str, access_token_secret: str, openai_api_key: str, target_username: str):
        # Clean username format (remove @ and any other special characters)
        self.target_username = target_username.replace("@", "").strip()
        logging.info(f"Initializing TwitterTranslator for user: {self.target_username}")
        
        try:
            # Create Client for v2 endpoints
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True
            )
            logging.info("Twitter client initialized successfully")
            
            # Get user ID from username using v2 endpoint
            user = self.client.get_user(username=self.target_username)
            if user.data:
                self.target_user_id = user.data.id
                logging.info(f"Found user ID: {self.target_user_id}")
            else:
                raise ValueError(f"Could not find user with username: {self.target_username}")
                
            # Set OpenAI API key
            openai.api_key = openai_api_key
            logging.info("OpenAI API key configured")
            
        except Exception as e:
            logging.error(f"Error initializing TwitterTranslator: {str(e)}")
            raise
        
    async def translate_text(self, text: str, max_retries: int = 3) -> Optional[str]:
        """Translate Chinese text to English using OpenAI's GPT model."""
        for attempt in range(max_retries):
            try:
                logging.info(f"Attempting translation (attempt {attempt + 1}/{max_retries})")
                response = await openai.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a professional translator. Translate the following Chinese text to English. Maintain the original meaning and tone."},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.3,  # Lower temperature for more consistent translations
                    timeout=30  # Set timeout to 30 seconds
                )
                translation = response.choices[0].message.content
                logging.info(f"Translation successful: {translation}")
                return translation
            except openai.error.RateLimitError:
                wait_time = (attempt + 1) * 5  # Exponential backoff
                logging.warning(f"Rate limit hit, waiting {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            except openai.error.APIError as e:
                logging.error(f"OpenAI API error: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                continue
            except Exception as e:
                logging.error(f"Translation error: {e}")
                return None
        logging.error("Max retries reached for translation")
        return None

    async def process_tweet(self, tweet_id: str):
        """Process a single tweet - get it and translate if it's in Chinese."""
        try:
            # Get tweet with its text
            tweet = self.client.get_tweet(tweet_id, tweet_fields=['text'])
            if tweet and tweet.data:
                tweet_text = tweet.data.text
                # Check if tweet is in Chinese (simplified or traditional)
                if any('\u4e00' <= char <= '\u9fff' for char in tweet_text):
                    print(f"Found Chinese tweet: {tweet_text}")
                    translation = await self.translate_text(tweet_text)
                    if translation:
                        print(f"Translation: {translation}")
                        # Reply to the tweet with the translation
                        response = self.client.create_tweet(
                            text=f"English translation:\n{translation}",
                            in_reply_to_tweet_id=tweet_id
                        )
                        if response.data:
                            print(f"Successfully replied to tweet {tweet_id}")
                        else:
                            print(f"Failed to reply to tweet {tweet_id}")
        except Exception as e:
            print(f"Error processing tweet {tweet_id}: {str(e)}")

class TweetMonitor:
    def __init__(self, translator: TwitterTranslator, client: tweepy.Client, poll_interval: int = 60):
        self.translator = translator
        self.client = client
        self.poll_interval = poll_interval
        self.last_tweet_id = None
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.running = True

    async def process_new_tweets(self):
        """Process new tweets from the user."""
        try:
            # Get user's tweets
            tweets = self.client.get_users_tweets(
                self.translator.target_user_id,
                tweet_fields=['text', 'referenced_tweets'],
                max_results=5,  # Limit to recent tweets
                since_id=self.last_tweet_id
            )
            
            if not tweets.data:
                return
            
            # Update last tweet ID
            self.last_tweet_id = tweets.data[0].id
            
            for tweet in reversed(tweets.data):  # Process older tweets first
                # Skip replies and retweets
                if hasattr(tweet, 'referenced_tweets') and tweet.referenced_tweets:
                    continue
                
                # Check for Chinese characters
                if any('\u4e00' <= char <= '\u9fff' for char in tweet.text):
                    logging.info(f"Found Chinese tweet: {tweet.text}")
                    await self.translator.process_tweet(tweet.id)
                
        except Exception as e:
            logging.error(f"Error processing tweets: {str(e)}")

    async def run(self):
        """Run the tweet monitor."""
        logging.info(f"Starting tweet monitor for user @{self.translator.target_username}")
        
        while self.running:
            try:
                await self.process_new_tweets()
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logging.error(f"Error in monitor loop: {str(e)}")
                await asyncio.sleep(self.poll_interval)  # Wait before retrying

async def main():
    # Get credentials from environment variables
    TWITTER_BEARER_TOKEN = os.getenv("TwitterAPIbearertoken")
    TWITTER_API_KEY = os.getenv("TwitterAPIKEY")
    TWITTER_API_SECRET = os.getenv("TwitterAPISecKEY")
    TWITTER_ACCESS_TOKEN = os.getenv("TwitterAPIAccesstoken")
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TwitterAPIAccesstokensecret")
    TARGET_USERNAME = os.getenv("Username")
    OPENAI_API_KEY = os.getenv("OpenaiAPI")
    
    # Set OpenAI API key in environment
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    
    required_vars = {
        "Bearer Token": TWITTER_BEARER_TOKEN,
        "API Key": TWITTER_API_KEY,
        "API Secret": TWITTER_API_SECRET,
        "Access Token": TWITTER_ACCESS_TOKEN,
        "Access Token Secret": TWITTER_ACCESS_TOKEN_SECRET,
        "Username": TARGET_USERNAME
    }
    
    missing_vars = [k for k, v in required_vars.items() if not v]
    if missing_vars:
        raise ValueError(f"Missing required credentials: {', '.join(missing_vars)}")
    
    logging.info("All required credentials found")
    
    if not OPENAI_API_KEY:
        print("Warning: No OpenAI API key found, translations may not work")

    translator = TwitterTranslator(
        TWITTER_BEARER_TOKEN,
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET,
        OPENAI_API_KEY,
        TARGET_USERNAME
    )
    
    # Initialize stream with bearer token
    stream = TweetStream(TWITTER_BEARER_TOKEN, translator)
    
    try:
        # Initialize Twitter client with API v2
        client = tweepy.Client(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
        
        # Initialize translator
        translator = TwitterTranslator(
            TWITTER_BEARER_TOKEN,
            TWITTER_API_KEY,
            TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN,
            TWITTER_ACCESS_TOKEN_SECRET,
            OPENAI_API_KEY,
            TARGET_USERNAME
        )
        
        # Initialize and run tweet monitor
        logging.info("Starting tweet monitor...")
        monitor = TweetMonitor(translator, client)
        
        try:
            await monitor.run()
        except KeyboardInterrupt:
            logging.info("Stopping monitor...")
            monitor.running = False
        
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Application stopped by user")
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        raise
