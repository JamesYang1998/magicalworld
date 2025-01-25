#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bot import TwitterBot
from src.llm import generate_response

def test_single_tweet():
    """
    Test posting a single tweet generated by GPT-4
    """
    try:
        print("Initializing Twitter bot...")
        bot = TwitterBot()
        
        print("\nGenerating tweet content using GPT-3.5-turbo...")
        tweet_content = generate_response("Generate a random interesting fact or thought in English.", model="gpt-3.5-turbo")
        
        print(f"\nPrepared tweet content: {tweet_content}")
        
        print("\nAttempting to post tweet...")
        try:
            response = bot.client.create_tweet(
                text=tweet_content
            )
            tweet_id = response.data['id']
            print(f"\nSuccess! Tweet posted successfully.")
            print(f"Tweet ID: {tweet_id}")
            print(f"Content: {tweet_content}")
            return True
        except Exception as e:
            print(f"Error posting tweet: {e}")
            return False
            
    except Exception as e:
        print(f"Error during test: {e}")
        return False

if __name__ == "__main__":
    test_single_tweet()
