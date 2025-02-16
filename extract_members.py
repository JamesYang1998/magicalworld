import re

def extract_usernames_from_text():
    """Extract usernames from the provided list of Twitter profiles"""
    usernames = set()
    
    # Usernames from screenshots
    raw_usernames = [
        'tomwanhh', '0xCheeezzyyyy', 'nftboi_', 'Neoo_Nav', 'based16z', 'Grantblocmates',
        'thedefiedge', 'gizmothegizzer', 'kwaker_oats_', 'purplepill3m', 'SmokeyTheBera',
        'rektdiomedes', 'juanaxyz00', 'jason_chen998', 'waleswoosh', 'DeFi_Cheetah',
        '0xGeeGee', 'beast_ico', 'stacy_muur', '2lambro', '0xelonmoney', 'Auri_0x',
        'whoiskevin', 'DeanKD', 'capykuro', '0xRacist', 'flb_xyz', 'oldmankotaro',
        'GuthixHL', 'TheOG_General'
    ]
    
    # Add cleaned usernames to set
    for username in raw_usernames:
        # Remove @ symbol if present
        clean_username = username.strip('@')
        if clean_username:
            usernames.add(clean_username)
    
    return sorted(list(usernames))

def main():
    usernames = extract_usernames_from_text()
    
    # Save to file
    filename = 'list_members_1882727258596450791.txt'
    with open(filename, 'w') as f:
        for username in usernames:
            f.write(f"{username}\n")
    
    print(f"Successfully saved {len(usernames)} usernames to {filename}")
    print("\nFirst 10 usernames for verification:")
    for username in usernames[:10]:
        print(f"@{username}")

if __name__ == "__main__":
    main()
