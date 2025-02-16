import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import random
import urllib3

# Disable SSL verification warnings globally
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TWITTER_ACCOUNTS = [
    'capykuro', 'PendleIntern', 'Thales_ai', 'TheOG_General', 'oldmankotaro', 
    'trackoor', 'MarioNawfal', 'kwantxbt', 'RedactedRes', 'wildbarestepf', 
    'drjasper_eth', 'elonmusk', 'Bloomberg', 'Cristiano', 'GuthixHL', '0xRacist', 
    'ibuyrugs', 'Togbe0x', 'basilda_a', 'flb_xyz', 'markets', 'shawmakesmagic', 
    'MarketWatch', 'katexbt', '0xMantleIntern', 'aixbt_agent', 'Cbb0fe', 'Forbes'
]

def get_tweet_time(time_str):
    """Convert relative time to datetime object"""
    now = datetime.now()
    if 'h' in time_str:
        hours = int(time_str.replace('h', ''))
        return now - timedelta(hours=hours)
    elif 'm' in time_str:
        minutes = int(time_str.replace('m', ''))
        return now - timedelta(minutes=minutes)
    return None

def get_tweets(username):
    """Fetch tweets for a given username using nitter instances"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)'
    }
    
    # Focus on most reliable Nitter instances
    nitter_instances = [
        'https://nitter.privacydev.net',  # Works well but needs rate limit handling
        'https://nitter.ktachibana.party',
        'https://nitter.in.projectsegfau.lt',
        'https://nitter.net'
    ]
    
    # Shuffle the instances to distribute load
    random.shuffle(nitter_instances)
    
    for instance in nitter_instances:
        url = f'{instance}/{username}'
        try:
            print(f"Trying {instance} for @{username}...")
            response = requests.get(url, headers=headers, timeout=15, verify=False)  # Disable SSL verification
            
            if response.status_code == 429:  # Rate limited
                print(f"Rate limited on {instance}, cooling down...")
                time.sleep(45)  # Longer cooldown for rate limits
                # Try the same instance again after cooldown
                response = requests.get(url, headers=headers, timeout=15, verify=False)
                if response.status_code == 200:
                    print(f"Successfully reconnected to {instance} after cooldown")
                else:
                    print(f"Still rate limited on {instance}, trying next instance...")
                    continue
            elif response.status_code == 404:  # Account not found
                print(f"Account not found on {instance}, might be suspended or renamed")
                continue
            elif response.status_code == 401:  # Unauthorized
                print(f"Access denied on {instance}, trying next instance...")
                continue
            elif response.status_code != 200:
                print(f"Failed to fetch tweets from {instance} for {username}. Status code: {response.status_code}")
                continue

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
                    
                    if datetime.now() - tweet_datetime <= timedelta(days=1):
                        tweets.append({
                            'username': username,
                            'content': content.text.strip(),
                            'timestamp': tweet_datetime,
                        })
                except Exception as e:
                    print(f"Error parsing tweet for {username}: {str(e)}")
                    continue
            
            if tweets:
                print(f"Successfully fetched {len(tweets)} tweets from {instance} for @{username}")
                return tweets
            
            print(f"No recent tweets found on {instance} for @{username}")
            
        except requests.exceptions.RequestException as e:
            print(f"Error accessing {instance} for {username}: {str(e)}")
            continue
        except Exception as e:
            print(f"Unexpected error for {username} on {instance}: {str(e)}")
            continue
    
    print(f"Failed to fetch tweets for {username} from all nitter instances")
    return []

def main():
    all_tweets = []
    total_accounts = len(TWITTER_ACCOUNTS)
    successful_accounts = 0
    print(f"Starting to crawl tweets from {total_accounts} accounts...")
    
    for idx, username in enumerate(TWITTER_ACCOUNTS, 1):
        print(f"\n[{idx}/{total_accounts}] Crawling tweets from @{username}...")
        try:
            tweets = get_tweets(username)
            all_tweets.extend(tweets)
            if tweets:
                successful_accounts += 1
                # Shorter delay if we successfully got tweets
                delay = random.uniform(5, 8)
            else:
                # Longer delay if we failed to get tweets to avoid rate limits
                delay = random.uniform(15, 20)
            
            print(f"Found {len(tweets)} recent tweets from @{username}")
            
            # Add delay between accounts
            if idx < total_accounts:
                print(f"Waiting {delay:.1f} seconds before next account...")
                time.sleep(delay)
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
