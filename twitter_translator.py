import tweepy
import openai
import asyncio
import os
from typing import Optional

class TwitterTranslator:
    def __init__(self, bearer_token: str, api_key: str, api_secret: str, 
                 access_token: str, access_token_secret: str, openai_api_key: str, target_username: str):
        # Clean username format (remove @ and any other special characters)
        clean_username = target_username.replace("@", "").split("_")[0]
        
        # Create Client for v2 endpoints
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # Get user ID from username using v2 endpoint
        user = self.client.get_user(username=clean_username)
        if user.data:
            self.target_user_id = user.data.id
            self.target_username = clean_username
        else:
            raise ValueError(f"Could not find user with username: {clean_username}")
            
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
        # Only process tweets from our target user
        if tweet.author_id == self.translator.target_user_id:
            self.loop.create_task(self.translator.process_tweet(tweet.id))

def main():
    # Get credentials from environment variables
    TWITTER_BEARER_TOKEN = os.getenv("TwitterAPIbearertoken")
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
