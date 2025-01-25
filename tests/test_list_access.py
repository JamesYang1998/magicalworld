import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bot import TwitterBot

def test_list_access():
    bot = TwitterBot()
    list_id = "1872292999155040454"
    
    print(f"Attempting to fetch members from list {list_id}...")
    success = bot.get_list_members(list_id)
    
    if success:
        print(f"Successfully fetched {len(bot.monitored_users)} users from the list:")
        for user_id, username in bot.monitored_users.items():
            print(f"- @{username} (ID: {user_id})")
    else:
        print("Failed to fetch list members")

if __name__ == "__main__":
    test_list_access()
