import tweepy
import openai
import asyncio
import os
from typing import Optional

class TwitterTranslator:
    def __init__(self, api_key: str, api_secret: str, 
                 access_token: str, access_token_secret: str, openai_api_key: str, target_username: str):
        # Clean username format (remove @ and any other special characters)
        clean_username = target_username.replace("@", "").split("_")[0]
        
        # Initialize Twitter API v1.1 authentication
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        
        # Create API object for v1.1 endpoints
        self.api = tweepy.API(auth)
        
        # Create Client for v2 endpoints
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # Get user ID from username
        user = self.api.get_user(screen_name=clean_username)
        self.target_user_id = user.id
        self.target_username = clean_username
        openai.api_key = openai_api_key
        
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
        tweet = self.client.get_tweet(tweet_id)
        if tweet and tweet.data:
            # Check if tweet is in Chinese (simplified or traditional)
            if any('\u4e00' <= char <= '\u9fff' for char in tweet.data.text):
                translation = await self.translate_text(tweet.data.text)
                if translation:
                    # Reply to the tweet with the translation
                    self.client.create_tweet(
                        text=f"English translation:\n{translation}",
                        in_reply_to_tweet_id=tweet_id
                    )

class TweetStream(tweepy.Stream):
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str, translator: TwitterTranslator):
        super().__init__(api_key, api_secret, access_token, access_token_secret)
        self.translator = translator
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def on_status(self, status):
        """Called when a tweet is received."""
        # Only process tweets from our target user
        if status.user.id == self.translator.target_user_id:
            self.loop.create_task(self.translator.process_tweet(status.id))

def main():
    # Get credentials from environment variables
    TWITTER_API_KEY = os.getenv("TwitterAPIKEY")
    TWITTER_API_SECRET = os.getenv("TwitterAPISecKEY")
    TWITTER_ACCESS_TOKEN = os.getenv("TwitterAPIAccesstoken")
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TwitterAPIAccesstokensecret")
    TARGET_USERNAME = os.getenv("Username")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Will use default OpenAI key from environment
    
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET,
                TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET,
                TARGET_USERNAME]):
        raise ValueError("Missing required Twitter credentials or username")
    
    if not OPENAI_API_KEY:
        print("Warning: No OpenAI API key found, translations may not work")

    translator = TwitterTranslator(
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET,
        OPENAI_API_KEY,
        TARGET_USERNAME
    )
    
    # Initialize stream with API credentials
    stream = TweetStream(
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET,
        translator
    )
    
    try:
        print(f"Starting stream to monitor tweets from @{TARGET_USERNAME}")
        # Filter for tweets from the target user
        stream.filter(follow=[str(translator.target_user_id)])
    except KeyboardInterrupt:
        print("\nStopping stream...")
        stream.disconnect()
    except Exception as e:
        print(f"Error: {e}")
        stream.disconnect()

if __name__ == "__main__":
    main()
