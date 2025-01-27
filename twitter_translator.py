import tweepy
import openai
import asyncio
import os
import logging
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
        
    async def translate_text(self, text: str) -> Optional[str]:
        """Translate Chinese text to English using OpenAI's GPT model."""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional translator. Translate the following Chinese text to English. Maintain the original meaning and tone."},
                    {"role": "user", "content": text}
                ],
                temperature=0.3  # Lower temperature for more consistent translations
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Translation error: {e}")
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

class TweetStream(tweepy.StreamingClient):
    def __init__(self, bearer_token: str, translator: TwitterTranslator):
        super().__init__(bearer_token)
        self.translator = translator
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def on_tweet(self, tweet):
        """Called when a tweet is received."""
        try:
            logging.info(f"Received tweet: {tweet.data}")
            # Only process tweets from our target user
            if tweet.author_id == self.translator.target_user_id:
                logging.info(f"Processing tweet from target user: {tweet.id}")
                self.loop.create_task(self.translator.process_tweet(tweet.id))
            else:
                logging.debug(f"Ignoring tweet from non-target user: {tweet.author_id}")
        except Exception as e:
            logging.error(f"Error in on_tweet: {str(e)}")

def main():
    # Get credentials from environment variables
    TWITTER_BEARER_TOKEN = os.getenv("TwitterAPIbearertoken")
    TWITTER_API_KEY = os.getenv("TwitterAPIKEY")
    TWITTER_API_SECRET = os.getenv("TwitterAPISecKEY")
    TWITTER_ACCESS_TOKEN = os.getenv("TwitterAPIAccesstoken")
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TwitterAPIAccesstokensecret")
    TARGET_USERNAME = os.getenv("Username")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Will use default OpenAI key from environment
    
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
        print(f"Starting stream to monitor tweets from @{TARGET_USERNAME}")
        # Set up filter rule for the target user
        # First, delete any existing rules
        rules = stream.get_rules()
        if rules and rules.data:
            rule_ids = [rule.id for rule in rules.data]
            stream.delete_rules(rule_ids)
        
        # Add new rule to follow target user
        stream.add_rules(tweepy.StreamRule(f"from:{translator.target_username}"))
        
        # Start filtering
        stream.filter(tweet_fields=["author_id", "text"])
    except KeyboardInterrupt:
        print("\nStopping stream...")
        stream.disconnect()
    except Exception as e:
        print(f"Error: {e}")
        stream.disconnect()

if __name__ == "__main__":
    main()
