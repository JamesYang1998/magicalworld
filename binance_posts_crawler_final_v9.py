import requests
import feedparser
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import random
import urllib3
from typing import List, Dict, Any
import re

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def parse_number(text: str) -> int:
    """Parse number from text with K/M suffixes"""
    if not text:
        return 0
    
    text = text.strip().lower()
    multiplier = 1
    
    if 'k' in text:
        multiplier = 1000
        text = text.replace('k', '')
    elif 'm' in text:
        multiplier = 1000000
        text = text.replace('m', '')
    
    try:
        return int(float(text) * multiplier)
    except:
        return 0

def extract_stats(soup: BeautifulSoup) -> Dict[str, int]:
    """Extract engagement stats from tweet HTML"""
    stats = {
        'replies': 0,
        'retweets': 0,
        'likes': 0,
        'quotes': 0
    }
    
    try:
        stats_div = soup.find('div', class_='tweet-stats')
        if stats_div:
            for stat in stats_div.find_all('div', class_='tweet-stat'):
                stat_text = stat.get_text().strip()
                stat_link = stat.find('a')
                
                if stat_link:
                    stat_title = stat_link.get('title', '').lower()
                    if 'repl' in stat_title:
                        stats['replies'] = parse_number(stat_text)
                    elif 'retweet' in stat_title:
                        stats['retweets'] = parse_number(stat_text)
                    elif 'like' in stat_title:
                        stats['likes'] = parse_number(stat_text)
                    elif 'quote' in stat_title:
                        stats['quotes'] = parse_number(stat_text)
    except:
        pass
    
    return stats

def get_posts(username: str, months: int = 3) -> List[Dict[str, Any]]:
    """Fetch all types of posts using Nitter RSS feeds"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
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
        'https://nitter.salastil.com'
    ]
    
    posts = []
    page = 1
    max_pages = 100
    
    while page <= max_pages:
        found_working_instance = False
        
        for instance in instances:
            try:
                url = f"{instance}/{username}"
                if page > 1:
                    url = f"{instance}/{username}/page/{page}"
                print(f"Trying {instance} page {page}...")
                
                response = requests.get(url, headers=headers, timeout=15, verify=False)
                
                if response.status_code != 200:
                    print(f"Failed to fetch page from {instance}. Status: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                tweets = soup.find_all('div', class_='timeline-item')
                
                if not tweets:
                    print(f"No tweets found on {instance} page {page}")
                    continue
                
                print(f"Found {len(tweets)} tweets")
                found_posts = False
                all_old = True
                
                for tweet in tweets:
                    try:
                        # Get timestamp
                        time_element = tweet.find('span', class_='tweet-date')
                        if not time_element:
                            continue
                        
                        time_link = time_element.find('a')
                        if not time_link or 'title' not in time_link.attrs:
                            continue
                        
                        tweet_time = time_link['title']
                        published = datetime.strptime(tweet_time, '%b %d, %Y · %I:%M %p UTC')
                        
                        # Check timeframe
                        if published < datetime.now() - timedelta(days=90):
                            continue
                        
                        all_old = False
                        
                        # Get content
                        content_div = tweet.find('div', class_='tweet-content')
                        if not content_div:
                            continue
                        
                        content = content_div.get_text().strip()
                        
                        # Determine post type and extract original author
                        post_type = 'Post'
                        original_author = None
                        
                        reply_div = tweet.find('div', class_='replying-to')
                        retweet_header = tweet.find('div', class_='retweet-header')
                        quote_link = tweet.find('a', class_='quote-link')
                        
                        if reply_div:
                            post_type = 'Reply'
                            reply_link = reply_div.find('a')
                            if reply_link:
                                original_author = reply_link.get_text().strip().replace('@', '')
                        elif retweet_header:
                            post_type = 'Retweet'
                            rt_text = retweet_header.get_text().strip()
                            rt_match = re.search(r'RT by @\w+: (@\w+):', rt_text)
                            if rt_match:
                                original_author = rt_match.group(1).replace('@', '')
                        elif quote_link:
                            post_type = 'Quote Tweet'
                            original_author = quote_link.get_text().strip().replace('@', '')
                        
                        # Get engagement metrics
                        engagement = extract_stats(tweet)
                        
                        posts.append({
                            'timestamp': published,
                            'content': content,
                            'type': post_type,
                            'original_author': original_author,
                            'replies': engagement['replies'],
                            'retweets': engagement['retweets'],
                            'likes': engagement['likes'],
                            'quotes': engagement['quotes']
                        })
                        found_posts = True
                        print(f"Found {post_type} from {published}")
                        if original_author:
                            print(f"Original author: @{original_author}")
                        print(f"Engagement: {engagement}")
                    
                    except Exception as e:
                        print(f"Error parsing tweet: {str(e)}")
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
