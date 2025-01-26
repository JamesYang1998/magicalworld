#!/usr/bin/env python3

from src.bot import TwitterBot
from src.logger import setup_logger


logger = setup_logger('run_bot')


def main():
    bot = TwitterBot()
    list_ids = ['1872292999155040454', '1882727258596450791']
    logger.info('Starting Twitter bot with GPT-4 integration...')
    logger.info(f'Monitoring lists: {", ".join(list_ids)}')
    logger.info(f'Maximum replies per user per day: {bot.max_daily_replies}')
    bot.monitor_multiple_lists(list_ids)


if __name__ == '__main__':
    main()
