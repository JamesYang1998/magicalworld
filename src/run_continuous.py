import os
import time
import signal
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from .bot import TwitterBot
from .logger import setup_logger

running = True
logger = None

def signal_handler(sig, frame):
    """Handle termination signals."""
    global running
    if logger:
        logger.info("Received signal to terminate")
    running = False
    sys.exit(0)

def run_bot_with_restart():
    """Run the bot with error handling and automatic restart."""
    global logger
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    load_dotenv()
    
    logger = setup_logger("continuous_bot")
    
    list_id = "1234567890"
    
    sts_dir = None
    if len(sys.argv) > 1:
        sts_dir = sys.argv[1]
    
    retry_count = 0
    max_retries = 5
    cooldown_time = 300  # 5 minutes
    
    logger.info("Starting Twitter bot with continuous operation")
    
    while running:
        try:
            bot = TwitterBot(sts_dir=sts_dir)
            bot.monitor_list_tweets(list_id, interval=60)
            
            retry_count = 0
            
        except Exception as e:
            logger.error(f"Bot crashed with error: {str(e)}")
            
            retry_count += 1
            
            if retry_count >= max_retries:
                logger.error(f"Maximum retries ({max_retries}) reached. Cooling down for {cooldown_time} seconds")
                time.sleep(cooldown_time)
                retry_count = 0
            else:
                wait_time = 30 * (2 ** (retry_count - 1))
                logger.info(f"Restarting in {wait_time} seconds (attempt {retry_count}/{max_retries})")
                time.sleep(wait_time)

if __name__ == "__main__":
    run_bot_with_restart()
