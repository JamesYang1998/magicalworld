import os
import sys
from dotenv import load_dotenv
from .bot import TwitterBot

def main():
    """Main function to start the Twitter bot."""
    load_dotenv()
    
    list_id = "1234567890"
    
    sts_dir = None
    if len(sys.argv) > 1:
        sts_dir = sys.argv[1]
    
    bot = TwitterBot(sts_dir=sts_dir)
    bot.monitor_list_tweets(list_id, interval=60)

if __name__ == "__main__":
    main()
