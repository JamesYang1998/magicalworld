from dotenv import load_dotenv
import os
import sys

def verify_environment():
    load_dotenv()
    
    required_vars = [
        'TWITTER_BEARER_TOKEN',
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET',
        'OPENAI_API_KEY'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)
    
    print('Environment variables loaded successfully')
    sys.exit(0)

if __name__ == '__main__':
    verify_environment()
