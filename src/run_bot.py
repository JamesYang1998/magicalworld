#!/usr/bin/env python3

from src.bot import TwitterBot
from src.logger import setup_logger


logger = setup_logger('run_bot')


def main():
    bot = TwitterBot()
    list_id = '1872292999155040454'
    logger.info('Starting Twitter bot with GPT-4 integration...')
    logger.info(f'Monitoring list: {list_id}')
    logger.info(f'Maximum replies per user per day: {bot.max_daily_replies}')
    bot.monitor_list_tweets(list_id)


if __name__ == '__main__':
    main()
