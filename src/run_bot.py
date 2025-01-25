#!/usr/bin/env python3

from .bot import TwitterBot

def main():
    bot = TwitterBot()
    list_id = '1872292999155040454'
    print('Starting Twitter bot with GPT-4 integration...')
    print('Monitoring list:', list_id)
    print('Maximum replies per user per day:', bot.max_daily_replies)
    bot.monitor_list_tweets(list_id)

if __name__ == '__main__':
    main()
