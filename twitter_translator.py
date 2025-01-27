import tweepy
from openai import AsyncOpenAI
import asyncio
import os
import logging
import time
from datetime import datetime
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
        logging.info(f"Monitoring tweets for user: @{self.target_username}")
        
        # Initialize rate limiting parameters
        self.rate_limit_window = 15 * 60  # 15 minutes in seconds
        self.max_requests = 50  # Maximum requests per window
        self.request_timestamps = []
        
        try:
            # Create Client for v2 endpoints with write permissions
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True,
                return_type=dict  # For better error handling
            )
            logging.info("Twitter API clients initialized")
            
            # Test authentication and get user info
            try:
                logging.info("Initializing Twitter API v2 clients...")
                
                # Log credential format for debugging (without exposing actual values)
                logging.info("Checking credential formats:")
                logging.info(f"Bearer token length: {len(bearer_token) if bearer_token else 0}")
                logging.info(f"API key length: {len(api_key) if api_key else 0}")
                logging.info(f"API secret length: {len(api_secret) if api_secret else 0}")
                logging.info(f"Access token length: {len(access_token) if access_token else 0}")
                logging.info(f"Access token secret length: {len(access_token_secret) if access_token_secret else 0}")
                
                # Initialize client with OAuth 2.0 App-Only authentication
                logging.info("Setting up OAuth 2.0 App-Only authentication...")
                self.app_client = tweepy.Client(bearer_token=bearer_token)
                
                # Test app-only authentication with error handling
                try:
                    # Test authentication with a simple user lookup instead
                    test_response = self.app_client.get_user(username=self.target_username)
                    logging.debug(f"App-Only auth test response type: {type(test_response)}")
                    
                    if test_response is not None:
                        logging.info("OAuth 2.0 App-Only authentication successful")
                        if isinstance(test_response, dict):
                            if 'data' in test_response:
                                logging.debug("Response has 'data' field")
                                logging.info(f"Successfully verified access to user @{self.target_username}")
                            if 'meta' in test_response:
                                logging.debug("Response has 'meta' field")
                        else:
                            if hasattr(test_response, 'data'):
                                logging.debug("Response has 'data' attribute")
                                logging.info(f"Successfully verified access to user @{self.target_username}")
                    else:
                        raise tweepy.errors.TweepyException("Empty response from Twitter API")
                except tweepy.errors.Unauthorized as e:
                    logging.error(f"App-Only authentication unauthorized: {str(e)}")
                    logging.error("Please verify your Bearer Token is valid and has the correct permissions")
                    raise
                except tweepy.errors.TooManyRequests as e:
                    logging.error(f"Rate limit exceeded during authentication test: {str(e)}")
                    logging.error("Please wait a few minutes and try again")
                    raise
                except tweepy.errors.TweepyException as e:
                    logging.error(f"App-Only authentication failed with TweepyException: {str(e)}")
                    logging.error("Please check your Twitter Developer Portal settings")
                    raise
                except Exception as e:
                    logging.error(f"App-Only authentication failed with unexpected error: {str(e)}")
                    logging.error("Please verify all credentials and API access levels")
                    raise tweepy.errors.TweepyException(f"Unexpected error during authentication: {str(e)}")
                
                # Set up OAuth 1.0a User Context authentication for write operations
                logging.info("Setting up OAuth 1.0a User Context authentication...")
                self.user_client = tweepy.Client(
                    consumer_key=api_key,
                    consumer_secret=api_secret,
                    access_token=access_token,
                    access_token_secret=access_token_secret,
                    wait_on_rate_limit=True  # Add automatic rate limit handling
                )
                
                # Store the app client as the default client for read operations
                self.client = self.app_client
                self.user_auth_working = False
                
                # Test user authentication but don't fail if it doesn't work
                try:
                    me = self.user_client.get_me()
                    logging.debug(f"User auth response: {me}")
                    
                    if me:
                        logging.debug(f"User auth response type: {type(me)}")
                        logging.debug(f"User auth response attributes: {dir(me)}")
                        if hasattr(me, 'data') and me.data:
                            auth_username = me.data.username
                            logging.info(f"OAuth 1.0a authentication successful as @{auth_username}")
                            self.user_auth_working = True
                        else:
                            logging.warning("OAuth 1.0a response missing expected data structure")
                    else:
                        logging.warning("OAuth 1.0a authentication returned empty response")
                except tweepy.errors.Unauthorized as e:
                    logging.warning(f"OAuth 1.0a authentication unauthorized: {str(e)}")
                except tweepy.errors.TweepyException as e:
                    logging.warning(f"OAuth 1.0a authentication failed with TweepyException: {str(e)}")
                except Exception as e:
                    logging.warning(f"OAuth 1.0a authentication failed with unexpected error: {str(e)}")
                
                if not self.user_auth_working:
                    logging.warning("User authentication not working - replies will be disabled")
                    logging.warning("Please verify Twitter Developer Portal settings:")
                    logging.warning("1. Check that OAuth 1.0a is enabled")
                    logging.warning("2. Verify Read and Write permissions are granted")
                    logging.warning("3. Confirm Access Token has correct permissions")
                    
                    # Test write permissions
                    logging.info("Testing write permissions...")
                    try:
                        test_tweets = self.client.get_users_tweets(
                            me['data']['id'],
                            max_results=1,
                            tweet_fields=['author_id']
                        )
                        if test_tweets and ('data' in test_tweets or 'meta' in test_tweets):
                            logging.info("Write permissions verified")
                        else:
                            logging.warning("Could not verify write permissions - response format unexpected")
                    except Exception as write_error:
                        logging.warning(f"Write permissions test failed: {str(write_error)}")
                        logging.warning("This may indicate insufficient API access level")
                        logging.warning("Error details: " + str(write_error))
                else:
                    raise tweepy.errors.Unauthorized("Failed to get user info - OAuth 1.0a authentication failed")
            except tweepy.errors.Unauthorized as auth_error:
                logging.error(f"Authentication failed with error: {str(auth_error)}")
                logging.error("Please verify your Twitter API credentials and access level (Elevated access required)")
                logging.error("Current credentials status:")
                logging.error(f"  Bearer token present: {bool(bearer_token)}")
                logging.error(f"  API key present: {bool(api_key)}")
                logging.error(f"  API secret present: {bool(api_secret)}")
                logging.error(f"  Access token present: {bool(access_token)}")
                logging.error(f"  Access token secret present: {bool(access_token_secret)}")
                raise
            except Exception as auth_error:
                logging.error(f"Authentication test failed with unexpected error: {str(auth_error)}")
                logging.error("Please check your Twitter Developer Portal for API status and permissions")
                raise
            
            # Get user ID from username using v2 endpoint
            user = self.client.get_user(username=self.target_username)
            if user and 'data' in user:
                self.target_user_id = user['data']['id']
                logging.info(f"Successfully found target user @{self.target_username}")
            else:
                raise ValueError(f"Could not find user @{self.target_username}")
                
            # Initialize OpenAI client
            self.openai_client = AsyncOpenAI(api_key=openai_api_key)
            logging.info("Translation service configured")
            
        except Exception as e:
            logging.error(f"Error initializing TwitterTranslator: {str(e)}")
            raise
        
    async def translate_text(self, text: str, max_retries: int = 3) -> Optional[str]:
        """Translate Chinese text to English using OpenAI's GPT model."""
        for attempt in range(max_retries):
            try:
                logging.info(f"Attempting translation (attempt {attempt + 1}/{max_retries})")
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a professional translator. Translate the following Chinese text to English. Maintain the original meaning and tone."},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.3  # Lower temperature for more consistent translations
                )
                translation = response.choices[0].message.content
                logging.info("Translation completed successfully")
                return translation
            except Exception as e:
                if "rate_limit" in str(e).lower():
                    wait_time = (attempt + 1) * 5  # Exponential backoff
                    logging.warning(f"Rate limit hit, waiting {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                elif "api" in str(e).lower():
                    logging.error(f"OpenAI API error: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2)
                    continue
            except Exception as e:
                logging.error(f"Translation error: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                    continue
                return None
        logging.error("Max retries reached for translation")
        return None

    async def process_tweet(self, tweet_id: str, max_retries: int = 3):
        """Process a single tweet - get it and translate if it's in Chinese."""
        try:
            # Check rate limits
            current_time = time.time()
            self.request_timestamps = [ts for ts in self.request_timestamps 
                                    if current_time - ts < self.rate_limit_window]
            if len(self.request_timestamps) >= self.max_requests:
                wait_time = self.rate_limit_window - (current_time - self.request_timestamps[0])
                logging.warning(f"Rate limit approaching, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
            
            # Get tweet with exponential backoff retry
            tweet = None
            last_error = None
            for attempt in range(max_retries):
                try:
                    tweet = self.client.get_tweet(
                        tweet_id,
                        tweet_fields=['text', 'author_id', 'conversation_id'],
                        user_auth=True
                    )
                    if tweet and 'data' in tweet:
                        break
                except tweepy.errors.TooManyRequests as e:
                    wait_time = 2 ** attempt
                    logging.warning(f"Rate limit hit, waiting {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    last_error = e
                except tweepy.errors.Unauthorized as e:
                    logging.error("Authentication error while fetching tweet")
                    raise
                except Exception as e:
                    wait_time = 2 ** attempt
                    logging.warning(f"Error fetching tweet (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(wait_time)
                    last_error = e
            
            if not tweet:
                if last_error:
                    raise last_error
                raise Exception("Failed to fetch tweet after retries")
                
            self.request_timestamps.append(time.time())
            
            if tweet and 'data' in tweet:
                tweet_text = tweet['data']['text']
                # Check if tweet is in Chinese (simplified or traditional)
                if any('\u4e00' <= char <= '\u9fff' for char in tweet_text):
                    logging.info(f"Processing Chinese tweet (ID: {tweet_id})")
                    translation = await self.translate_text(tweet_text)
                    if translation:
                        logging.info("Preparing to post translation reply")
                        max_retries = 3
                        retry_delay = 1
                        
                        for attempt in range(max_retries):
                            try:
                                # Reply to the tweet using v2 API
                                reply_text = f"English translation:\n{translation}"
                                
                                # Post the reply using v2 endpoint
                                # Check if user authentication is working before attempting to reply
                                if not self.user_auth_working:
                                    logging.warning("Cannot post reply: User authentication not working")
                                    logging.warning("Please check Twitter Developer Portal settings and update credentials")
                                    return
                                
                                # Post reply with exponential backoff retry using user client
                                response = None
                                for reply_attempt in range(max_retries):
                                    try:
                                        response = self.user_client.create_tweet(
                                            text=reply_text,
                                            in_reply_to_tweet_id=tweet_id
                                        )
                                        if response and 'data' in response:
                                            logging.info(f"Successfully posted reply to tweet {tweet_id}")
                                            break
                                    except tweepy.errors.TooManyRequests:
                                        wait_time = 2 ** reply_attempt
                                        logging.warning(f"Rate limit hit while posting reply, waiting {wait_time} seconds...")
                                        await asyncio.sleep(wait_time)
                                    except tweepy.errors.Unauthorized:
                                        logging.error("Authentication error while posting reply - please check Twitter Developer Portal settings")
                                        self.user_auth_working = False
                                        return
                                    except Exception as reply_error:
                                        wait_time = 2 ** reply_attempt
                                        logging.warning(f"Error posting reply (attempt {reply_attempt + 1}/{max_retries}): {str(reply_error)}")
                                        if reply_attempt < max_retries - 1:
                                            await asyncio.sleep(wait_time)
                                        else:
                                            logging.error("Failed to post reply after all retries")
                                            return
                                
                                if response and 'data' in response:
                                    reply_id = response['data']['id']
                                    logging.info(f"Successfully posted translation reply (ID: {reply_id}) to tweet {tweet_id}")
                                    break
                                else:
                                    logging.error("Failed to create reply tweet - no response data")
                                    
                            except tweepy.errors.TooManyRequests as rate_error:
                                if attempt < max_retries - 1:
                                    wait_time = retry_delay * (2 ** attempt)
                                    logging.warning(f"Rate limit hit, waiting {wait_time} seconds...")
                                    await asyncio.sleep(wait_time)
                                else:
                                    logging.error("Max retries reached for rate limit")
                                    raise
                                    
                            except tweepy.errors.Unauthorized as auth_error:
                                logging.error(f"Authentication failed: {str(auth_error)}")
                                raise
                                
                            except tweepy.errors.BadRequest as bad_request:
                                logging.error(f"Bad request error: {str(bad_request)}")
                                raise
                                
                            except Exception as e:
                                if attempt < max_retries - 1:
                                    wait_time = retry_delay * (2 ** attempt)
                                    logging.warning(f"Error posting reply, retrying in {wait_time} seconds: {str(e)}")
                                    await asyncio.sleep(wait_time)
                                else:
                                    logging.error(f"Failed to post reply after {max_retries} attempts: {str(e)}")
                                    raise
                                    
        except Exception as e:
            logging.error(f"Error processing tweet {tweet_id}: {str(e)}")

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
                    logging.debug("Skipping retweet or reply")
                    continue
                
                # Check for Chinese characters
                if any('\u4e00' <= char <= '\u9fff' for char in tweet.text):
                    logging.info("Found tweet containing Chinese text")
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
        "Username": TARGET_USERNAME,
        "OpenAI API Key": OPENAI_API_KEY
    }
    
    missing_vars = [k for k, v in required_vars.items() if not v]
    if missing_vars:
        raise ValueError(f"Missing required credentials: {', '.join(missing_vars)}")
    
    logging.info("All required credentials found")
    
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
