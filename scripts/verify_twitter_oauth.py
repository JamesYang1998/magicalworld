import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twitter API credentials
TWITTER_CLIENT_ID = os.getenv("TWITTER_CLIENT_ID")
TWITTER_CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = os.getenv("TWITTER_API_KEY_SECRET")
TWITTER_REDIRECT_URI = os.getenv("TWITTER_REDIRECT_URI")

# Verify credentials
print(f"TWITTER_CLIENT_ID: {'Set' if TWITTER_CLIENT_ID else 'Not set'}")
print(f"TWITTER_CLIENT_SECRET: {'Set' if TWITTER_CLIENT_SECRET else 'Not set'}")
print(f"TWITTER_API_KEY: {'Set' if TWITTER_API_KEY else 'Not set'}")
print(f"TWITTER_API_KEY_SECRET: {'Set' if TWITTER_API_KEY_SECRET else 'Not set'}")
print(f"TWITTER_REDIRECT_URI: {'Set' if TWITTER_REDIRECT_URI else 'Not set'}")
