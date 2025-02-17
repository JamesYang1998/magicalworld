import requests
import feedparser
import pandas as pd
from datetime import datetime, timedelta
import time
import random
from typing import List, Dict, Any
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_posts(username: str, months: int = 3) -> List[Dict[str, Any]]:
    """Fetch posts and replies using Nitter RSS feeds"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml,application/xml;q=0.9',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    # Nitter instances with RSS support
    instances = [
        'https://nitter.net',
        'https://nitter.cz',
        'https://nitter.privacydev.net',
        'https://nitter.foss.wtf',
        'https://nitter.1d4.us'
    ]
    
    posts = []
    cutoff_date = datetime.now() - timedelta(days=months*30)
    
    for instance in instances:
        try:
            url = f"{instance}/{username}/rss"
            print(f"Trying {instance} RSS feed...")
            
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            
            if response.status_code != 200:
                print(f"Failed to fetch RSS feed from {instance}. Status: {response.status_code}")
                continue
            
            feed = feedparser.parse(response.text)
            
            if not feed.entries:
                print(f"No entries found in RSS feed from {instance}")
                continue
            
            print(f"Found {len(feed.entries)} entries in RSS feed")
            
            for entry in feed.entries:
                try:
                    # Parse timestamp
                    published = datetime(*entry.published_parsed[:6])
                    
                    # Check timeframe
                    if published < cutoff_date:
                        continue
                    
                    # Get content and type
                    content = entry.description
                    is_reply = 'R to @' in entry.title
                    
                    # Extract engagement metrics from content
                    engagement = {
                        'replies': 0,
                        'retweets': 0,
                        'likes': 0,
                        'quotes': 0
                    }
                    
                    # Try to parse engagement metrics from HTML content
                    if '<span class="tweet-stat">' in content:
                        for stat in content.split('<span class="tweet-stat">'):
                            if 'Replies:' in stat:
                                engagement['replies'] = int(''.join(filter(str.isdigit, stat.split('</span>')[0])) or 0)
                            elif 'Retweets:' in stat:
                                engagement['retweets'] = int(''.join(filter(str.isdigit, stat.split('</span>')[0])) or 0)
                            elif 'Likes:' in stat:
                                engagement['likes'] = int(''.join(filter(str.isdigit, stat.split('</span>')[0])) or 0)
                            elif 'Quotes:' in stat:
                                engagement['quotes'] = int(''.join(filter(str.isdigit, stat.split('</span>')[0])) or 0)
                    
                    # Clean content (remove HTML tags)
                    from bs4 import BeautifulSoup
                    clean_content = BeautifulSoup(content, 'html.parser').get_text()
                    
                    posts.append({
                        'timestamp': published,
                        'content': clean_content,
                        'type': 'Reply' if is_reply else 'Post',
                        'replies': engagement['replies'],
                        'retweets': engagement['retweets'],
                        'likes': engagement['likes'],
                        'quotes': engagement['quotes']
                    })
                    print(f"Found {'reply' if is_reply else 'post'} from {published}")
                
                except Exception as e:
                    print(f"Error parsing entry: {str(e)}")
                    continue
            
            if posts:
                print(f"Successfully fetched {len(posts)} posts from {instance}")
                break
            
        except Exception as e:
            print(f"Error accessing {instance}: {str(e)}")
            continue
    
    return posts

def save_to_excel(posts: List[Dict[str, Any]], username: str):
    """Save posts to Excel file with proper formatting"""
    if not posts:
        print("No posts to save.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(posts)
    
    # Sort by timestamp
    df = df.sort_values('timestamp', ascending=False)
    
    # Format timestamp
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Format numbers with K/M suffix
    for col in ['replies', 'retweets', 'likes', 'quotes']:
        df[col] = df[col].apply(lambda x: f"{x/1000000:.1f}M" if x >= 1000000 else (f"{x/1000:.1f}K" if x >= 1000 else str(int(x))))
    
    # Save to Excel
    filename = f'{username}_posts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    df.to_excel(filename, index=False, engine='openpyxl')
    
    print(f"\nSuccessfully saved {len(posts)} posts to {filename}")
    print(f"\nPost types distribution:\n{df['type'].value_counts()}")
    print("\nDate range:")
    print(f"Earliest: {df['timestamp'].min()}")
    print(f"Latest: {df['timestamp'].max()}")

def main():
    username = "cz_binance"
    months = 3
    print(f"Starting to crawl posts from @{username} for the past {months} months...")
    
    posts = get_posts(username, months)
    save_to_excel(posts, username)

if __name__ == "__main__":
    main()
