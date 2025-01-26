#!/usr/bin/env python3

import os
import sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bot import TwitterBot
from src.logger import setup_logger

logger = setup_logger('tweet_analyzer')

def analyze_user_tweets(username: str = "JimsYoung_", max_results: int = 100):
    """
    Fetch and analyze tweets from a specific user
    """
    try:
        bot = TwitterBot()
        
        # Get user ID first
        user = bot.client.get_user(username=username)
        if not user or not user.data:
            logger.error(f"Could not find user @{username}")
            return
            
        user_id = user.data.id
        logger.info(f"Found user @{username} with ID: {user_id}")
        
        # Fetch user's tweets
        tweets = bot.client.get_users_tweets(
            id=user_id,
            max_results=max_results,
            tweet_fields=['created_at', 'public_metrics', 'context_annotations']
        )
        
        if not tweets or not tweets.data:
            logger.info(f"No tweets found for @{username}")
            return
            
        logger.info(f"Found {len(tweets.data)} tweets to analyze")
        
        # Analyze tweets
        for tweet in tweets.data:
            logger.info("\nTweet Analysis:")
            logger.info(f"Date: {tweet.created_at}")
            logger.info(f"Content: {tweet.text}")
            if hasattr(tweet, 'public_metrics'):
                metrics = tweet.public_metrics
                logger.info(f"Metrics: {metrics}")
            logger.info("-" * 80)
            
        return tweets.data

    except Exception as e:
        logger.error(f"Error analyzing tweets: {e}", exc_info=True)
        return None

if __name__ == "__main__":
    analyze_user_tweets()
