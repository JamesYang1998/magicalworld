import tweepy
import openai
import asyncio
import os
from typing import Optional

class TwitterTranslator:
    def __init__(self, twitter_bearer_token: str, openai_api_key: str):
        self.client = tweepy.Client(bearer_token=twitter_bearer_token)
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
            if any('\u4e00' <= char <= '\u9fff' for char in tweet.data['text']):
                translation = await self.translate_text(tweet.data['text'])
                if translation:
                    # Here you would implement the logic to post or store the translation
                    print(f"Original: {tweet.data['text']}")
                    print(f"Translation: {translation}")

class TweetStream(tweepy.StreamingClient):
    def __init__(self, bearer_token: str, translator: TwitterTranslator):
        super().__init__(bearer_token)
        self.translator = translator
        self.loop = asyncio.get_event_loop()

    def on_tweet(self, tweet):
        """Called when a tweet is received."""
        self.loop.create_task(self.translator.process_tweet(tweet.id))

def main():
    # These would come from environment variables in production
    TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    if not all([TWITTER_BEARER_TOKEN, OPENAI_API_KEY]):
        raise ValueError("Missing required environment variables")

    translator = TwitterTranslator(TWITTER_BEARER_TOKEN, OPENAI_API_KEY)
    stream = TweetStream(TWITTER_BEARER_TOKEN, translator)
    
    # Filter for tweets that might be in Chinese
    stream.filter(track=["的", "是", "在"])  # Common Chinese characters

if __name__ == "__main__":
    main()
