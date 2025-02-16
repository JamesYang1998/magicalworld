import requests
from bs4 import BeautifulSoup
import urllib3
import time
import random

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_list_members(list_id: str) -> list:
    """Fetch members of a Twitter list using Nitter instances"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    
    # Most reliable Nitter instance
    instance = 'https://nitter.net'
    members = set()
    page = 1
    prev_member_count = 0
    target_count = 496  # From list info
    
    while True:
        print(f"Fetching page {page}...")
        try:
            # Use URL structure from screenshots
            url = f"{instance}/i/lists/{list_id}/members"
            if page > 1:
                url += f"/p/{page}"
            print(f"Fetching from {url}")
            
            response = requests.get(url, headers=headers, timeout=20, verify=False)
            
            if response.status_code == 429:  # Rate limited
                print("Rate limited, waiting 60 seconds...")
                time.sleep(60)
                continue
            elif response.status_code != 200:
                print(f"Failed to fetch members. Status code: {response.status_code}")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for profile cards
            profile_cards = soup.find_all('div', class_='profile-card')
            
            found_members = False
            for card in profile_cards:
                username_elem = card.find('a', class_='username')
                if username_elem and username_elem.text:
                    username = username_elem.text.strip().replace('@', '')
                    if username and username not in ['', 'undefined', 'null']:
                        members.add(username)
                        print(f"Found member: @{username}")
                        found_members = True
            
            if not found_members:
                print("No members found on this page.")
                if page > 1:  # If we've successfully fetched before but now got nothing
                    break
            
            # Check if we've found enough members
            if len(members) >= target_count:
                print(f"Found all {target_count} members, stopping...")
                break
            elif len(members) == prev_member_count and page > 1:
                print(f"No new members found after page {page}, stopping...")
                break
            
            prev_member_count = len(members)
            print(f"Found {len(members)} unique members so far...")
            
            page += 1
            time.sleep(random.uniform(2, 5))  # Random delay between pages
            
        except Exception as e:
            print(f"Error: {str(e)}")
            break
    
    return sorted(list(members))

def main():
    list_id = "1882727258596450791"
    print(f"Starting to crawl members from list {list_id}...")
    
    members = get_list_members(list_id)
    
    if members:
        filename = f'list_members_{list_id}.txt'
        with open(filename, 'w') as f:
            for member in members:
                f.write(f"{member}\n")
        print(f"\nSuccessfully saved {len(members)} members to {filename}")
    else:
        print("\nNo members found.")

if __name__ == "__main__":
    main()
