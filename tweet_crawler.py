import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import random
import urllib3
import concurrent.futures
from typing import List, Dict, Any

# Disable SSL verification warnings globally
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TWITTER_ACCOUNTS = [
    'capykuro', 'PendleIntern', 'Thales_ai', 'TheOG_General', 'oldmankotaro', 
    'trackoor', 'MarioNawfal', 'kwantxbt', 'RedactedRes', 'wildbarestepf', 
    'drjasper_eth', 'elonmusk', 'Bloomberg', 'Cristiano', 'GuthixHL', '0xRacist', 
    'ibuyrugs', 'Togbe0x', 'basilda_a', 'flb_xyz', 'markets', 'shawmakesmagic', 
    'MarketWatch', 'katexbt', '0xMantleIntern', 'aixbt_agent', 'Cbb0fe', 'Forbes'
]

def get_tweets(username: str, max_retries: int = 30) -> List[Dict[str, Any]]:
    """Fetch tweets for a given username using nitter instances with retries"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)'
    }
    
    # Multiple reliable instances with proven track record
    primary_instances = [
        'https://nitter.privacydev.net',   # Most reliable instance
        'https://nitter.cz',               # Czech instance
        'https://bird.trom.tf',            # Reliable backup
        'https://nitter.net',              # Official instance
        'https://nitter.fdn.fr',           # French instance
        'https://nitter.1d4.us'            # US instance
    ]
    
    for attempt in range(max_retries):
        # Rotate through instances systematically
        instance_index = attempt % len(primary_instances)
        current_instance = primary_instances[instance_index]
        
        if attempt > 0:
            print(f"Retry attempt {attempt + 1}/{max_retries} for @{username}")
            time.sleep(30 + (attempt % 6) * 15)  # Cycle delays every 6 attempts
        
        try:
            url = f'{current_instance}/{username}'
            print(f"Trying {current_instance} for @{username}...")
            response = requests.get(url, headers=headers, timeout=15, verify=False)
            
            if response.status_code == 429:  # Rate limited
                print(f"Rate limited on {current_instance}, cooling down...")
                time.sleep(90)  # Much longer cooldown for rate limits
                response = requests.get(url, headers=headers, timeout=15, verify=False)
                if response.status_code != 200:
                    print(f"Still rate limited on {current_instance}, trying next instance...")
                    continue
            elif response.status_code != 200:
                print(f"Failed to fetch tweets from {current_instance} for {username}. Status code: {response.status_code}")
                continue
            
            # Parse tweets from response
            soup = BeautifulSoup(response.text, 'html.parser')
            tweets = []
            
            for tweet in soup.find_all('div', class_='timeline-item'):
                try:
                    content = tweet.find('div', class_='tweet-content')
                    time_element = tweet.find('span', class_='tweet-date')
                    
                    if not content or not time_element:
                        continue
                    
                    tweet_time = time_element.find('a')['title']
                    tweet_datetime = datetime.strptime(tweet_time, '%b %d, %Y · %I:%M %p UTC')
                    
                    time_diff = datetime.now() - tweet_datetime
                    hours_ago = time_diff.total_seconds()/3600
                    
                    if hours_ago < 20.0:  # Even stricter 24-hour check
                        tweets.append({
                            'username': username,
                            'content': content.text.strip(),
                            'timestamp': tweet_datetime,
                        })
                        print(f"Found tweet from {hours_ago:.1f} hours ago (within 20.0h limit)")
                    else:
                        print(f"Skipping tweet from {hours_ago:.1f} hours ago (limit: 20.0h)")
                        if len(tweets) >= 2:  # Stop very early to avoid older tweets
                            break
                except Exception as e:
                    print(f"Error parsing tweet: {str(e)}")
                    continue
            
            if tweets:
                print(f"Successfully fetched {len(tweets)} tweets from {current_instance} for @{username}")
                return tweets
            
            print(f"No recent tweets found on {current_instance} for @{username}")
            
        except requests.exceptions.RequestException as e:
            print(f"Error accessing {current_instance} for {username}: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
    
    print(f"Failed to fetch tweets for {username} from all nitter instances")
    return []

def clean_old_tweets(tweets: List[Dict[str, Any]], max_age: float = 20.0) -> List[Dict[str, Any]]:
    """Clean tweets list to ensure strict time compliance"""
    now = datetime.now()
    cleaned = []
    for tweet in tweets:
        hours_old = (now - tweet['timestamp']).total_seconds() / 3600
        if hours_old < max_age:
            cleaned.append(tweet)
            print(f"Verified tweet from {hours_old:.1f} hours ago (passed final check)")
        else:
            print(f"Removing tweet from {hours_old:.1f} hours ago in final check")
    return cleaned

def process_account(username: str) -> List[Dict[str, Any]]:
    """Process a single Twitter account and return its tweets"""
    try:
        tweets = get_tweets(username)
        # Additional cleaning pass to ensure strict time compliance
        return clean_old_tweets(tweets)
    except Exception as e:
        print(f"Error processing account @{username}: {str(e)}")
        return []

def main():
    all_tweets = []
    total_accounts = len(TWITTER_ACCOUNTS)
    successful_accounts = 0
    print(f"Starting to crawl tweets from {total_accounts} accounts...")
    
    # Process accounts in parallel with a maximum of 1 worker to avoid rate limits
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        # Submit all accounts for processing
        future_to_username = {executor.submit(process_account, username): username 
                            for username in TWITTER_ACCOUNTS}
        
        # Process completed futures as they finish
        for future in concurrent.futures.as_completed(future_to_username):
            username = future_to_username[future]
            try:
                tweets = future.result()
                all_tweets.extend(tweets)
                if tweets:
                    successful_accounts += 1
                print(f"Found {len(tweets)} recent tweets from @{username}")
            except Exception as e:
                print(f"Error processing account @{username}: {str(e)}")
                continue
    
    print(f"\nCrawling complete! Processed {total_accounts} accounts.")
    print(f"Successfully fetched tweets from {successful_accounts} accounts.")
    print(f"Total tweets found: {len(all_tweets)}")
    
    if all_tweets:
        filename = f'tweets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df = pd.DataFrame(all_tweets)
        df.to_csv(filename, index=False)
        print(f"\nSuccessfully saved {len(all_tweets)} tweets to {filename}")
        print(f"CSV columns: {', '.join(df.columns)}")
        print(f"Tweet counts by user:\n{df['username'].value_counts()}")
    else:
        print("\nNo tweets were found in the last 24 hours.")

if __name__ == "__main__":
    main()
