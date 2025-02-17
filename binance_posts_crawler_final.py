import requests
import feedparser
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import random
import urllib3
from typing import List, Dict, Any

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_timestamp_from_string(time_str: str) -> datetime:
    """Convert timestamp string to datetime object"""
    try:
        return datetime.strptime(time_str, '%b %d, %Y · %I:%M %p UTC')
    except:
        return datetime.now()

def is_within_timeframe(timestamp: datetime, months: int = 3) -> bool:
    """Check if timestamp is within specified months from now"""
    cutoff_date = datetime.now() - timedelta(days=months*30)
    return timestamp >= cutoff_date

def get_posts(username: str, months: int = 3) -> List[Dict[str, Any]]:
    """Fetch all types of posts using Nitter RSS feeds"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml,application/xml;q=0.9',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    # Most reliable Nitter instances
    instances = [
        'https://nitter.privacydev.net',
        'https://nitter.pw',
        'https://nitter.poast.org',
        'https://nitter.bird.froth.zone',
        'https://nitter.datura.network',
        'https://nitter.tux.pizza',
        'https://nitter.salastil.com',
        'https://nitter.x86-64-unknown-linux-gnu.zip'
    ]
    
    posts = []
    page = 1
    max_pages = 100  # Increased page limit for more historical data
    
    while page <= max_pages:
        found_working_instance = False
        
        for instance in instances:
            try:
                url = f"{instance}/{username}/rss"
                if page > 1:
                    url = f"{instance}/{username}/page/{page}/rss"
                print(f"Trying {instance} page {page}...")
                
                response = requests.get(url, headers=headers, timeout=15, verify=False)
                
                if response.status_code != 200:
                    print(f"Failed to fetch RSS feed from {instance}. Status: {response.status_code}")
                    continue
                
                feed = feedparser.parse(response.text)
                
                if not feed.entries:
                    print(f"No entries found in RSS feed from {instance} page {page}")
                    continue
                
                print(f"Found {len(feed.entries)} entries in RSS feed")
                found_posts = False
                all_old = True
                
                for entry in feed.entries:
                    try:
                        # Parse timestamp
                        published = datetime(*entry.published_parsed[:6])
                        
                        # Check timeframe
                        if published < datetime.now() - timedelta(days=90):
                            continue
                        
                        all_old = False
                        
                        # Get content and type
                        content = entry.description
                        title = entry.title
                        
                        # Determine post type
                        post_type = 'Post'
                        if 'R to @' in title:
                            post_type = 'Reply'
                        elif 'RT by @' in title:
                            post_type = 'Retweet'
                        elif 'QT by @' in title:
                            post_type = 'Quote Tweet'
                        
                        # Extract engagement metrics from content
                        engagement = {
                            'replies': 0,
                            'retweets': 0,
                            'likes': 0,
                            'quotes': 0
                        }
                        
                        # Parse engagement metrics from HTML content
                        soup = BeautifulSoup(content, 'html.parser')
                        stats = soup.find_all('span', class_='tweet-stat')
                        
                        for stat in stats:
                            stat_text = stat.get_text().strip()
                            stat_title = stat.get('title', '').lower()
                            
                            try:
                                value = stat_text.strip().lower()
                                multiplier = 1
                                
                                if 'k' in value:
                                    multiplier = 1000
                                    value = value.replace('k', '')
                                elif 'm' in value:
                                    multiplier = 1000000
                                    value = value.replace('m', '')
                                
                                value = float(value) * multiplier
                                
                                if 'repl' in stat_title:
                                    engagement['replies'] = int(value)
                                elif 'retweet' in stat_title:
                                    engagement['retweets'] = int(value)
                                elif 'like' in stat_title:
                                    engagement['likes'] = int(value)
                                elif 'quote' in stat_title:
                                    engagement['quotes'] = int(value)
                            except:
                                continue
                        
                        # Clean content
                        clean_content = soup.get_text().strip()
                        
                        # Get original author for retweets
                        original_author = None
                        if post_type in ['Retweet', 'Quote Tweet']:
                            try:
                                author_match = soup.find('div', class_='retweet-header')
                                if author_match:
                                    original_author = author_match.get_text().strip()
                            except:
                                pass
                        
                        posts.append({
                            'timestamp': published,
                            'content': clean_content,
                            'type': post_type,
                            'original_author': original_author,
                            'replies': engagement['replies'],
                            'retweets': engagement['retweets'],
                            'likes': engagement['likes'],
                            'quotes': engagement['quotes']
                        })
                        found_posts = True
                        print(f"Found {post_type} from {published}")
                    
                    except Exception as e:
                        print(f"Error parsing entry: {str(e)}")
                        continue
                
                if found_posts:
                    found_working_instance = True
                    if all_old:
                        return posts
                    break
                
            except Exception as e:
                print(f"Error accessing {instance}: {str(e)}")
                continue
        
        if not found_working_instance:
            print("No working instances found")
            break
        
        page += 1
        time.sleep(random.uniform(2, 4))
    
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
    filename = f'{username}_posts_complete_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    df.to_excel(filename, index=False, engine='openpyxl')
    
    print(f"\nSuccessfully saved {len(posts)} posts to {filename}")
    print(f"\nPost types distribution:\n{df['type'].value_counts()}")
    print("\nDate range:")
    print(f"Earliest: {df['timestamp'].min()}")
    print(f"Latest: {df['timestamp'].max()}")
    
    return filename

def main():
    username = "cz_binance"
    months = 3
    print(f"Starting to crawl all content from @{username} for the past {months} months...")
    
    posts = get_posts(username, months)
    save_to_excel(posts, username)

if __name__ == "__main__":
    main()
