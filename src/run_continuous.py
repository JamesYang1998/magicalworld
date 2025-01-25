#!/usr/bin/env python3

import sys
import time
import traceback
from datetime import datetime
import signal
import os

from src.logger import setup_logger

logger = setup_logger('continuous_bot')

def signal_handler(signum, frame):
    logger.info("Received shutdown signal. Exiting gracefully...")
    sys.exit(0)

def run_bot_with_restart():
    """Run the bot continuously with automatic restart on errors"""
    from src.bot import TwitterBot
    
    max_retries = 3  # Maximum number of quick retries before cooling down
    retry_count = 0
    cooldown_time = 300  # 5 minutes cooldown after max retries
    
    while True:
        try:
            logger.info(f"=== Starting bot at {datetime.now()} ===")
            bot = TwitterBot()
            list_id = '1872292999155040454'
            logger.info('Twitter bot with GPT-4 integration initialized')
            logger.info(f'Monitoring list: {list_id}')
            logger.info(f'Maximum replies per user per day: {bot.max_daily_replies}')
            
            # Main monitoring loop
            bot.monitor_list_tweets(list_id)
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt. Shutting down gracefully...")
            sys.exit(0)
            
        except Exception as e:
            current_time = datetime.now()
            logger.error(f"Error occurred at {current_time}:", exc_info=True)
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            
            retry_count += 1
            if retry_count >= max_retries:
                logger.warning(f"Maximum retries ({max_retries}) reached. Entering cooldown period...")
                time.sleep(cooldown_time)
                retry_count = 0
            else:
                logger.info(f"Retrying in 60 seconds... (Attempt {retry_count}/{max_retries})")
                time.sleep(60)

if __name__ == '__main__':
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting continuous bot operation...")
    run_bot_with_restart()
