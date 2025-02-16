import pandas as pd
from datetime import datetime, timedelta
import glob
import os

# Find the most recent CSV file
csv_files = glob.glob('tweets_*.csv')
latest_csv = max(csv_files, key=os.path.getctime)

print(f"\nAnalyzing file: {latest_csv}")
print('-' * 50)

# Read the CSV file
df = pd.read_csv(latest_csv)

# Print basic information
print('\nDataset Overview:')
print('-' * 50)
print(f'Total tweets: {len(df)}')
print(f'Unique accounts: {df.username.nunique()}')
print(f'Columns present: {", ".join(df.columns)}')

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Convert timestamp to datetime and check time window
df['timestamp'] = pd.to_datetime(df['timestamp'])
now = pd.Timestamp.now()
time_diff = now - df['timestamp']
hours_old = time_diff / pd.Timedelta(hours=1)

print('\nTimestamp Analysis:')
print('-' * 50)
print(f'Oldest tweet: {df.timestamp.min()}')
print(f'Newest tweet: {df.timestamp.max()}')
print(f'All tweets within 24 hours: {all(hours_old < 24.0)}')
print(f'Tweets older than 24 hours: {sum(hours_old >= 24.0)}')

# Define expected accounts
EXPECTED_ACCOUNTS = [
    'capykuro', 'PendleIntern', 'Thales_ai', 'TheOG_General', 'oldmankotaro', 
    'trackoor', 'MarioNawfal', 'kwantxbt', 'RedactedRes', 'wildbarestepf', 
    'drjasper_eth', 'elonmusk', 'Bloomberg', 'Cristiano', 'GuthixHL', '0xRacist', 
    'ibuyrugs', 'Togbe0x', 'basilda_a', 'flb_xyz', 'markets', 'shawmakesmagic', 
    'MarketWatch', 'katexbt', '0xMantleIntern', 'aixbt_agent', 'Cbb0fe', 'Forbes'
]

# Check accounts
print('\nAccount Coverage:')
print('-' * 50)
found_accounts = set(df.username.unique())
expected_accounts = set(EXPECTED_ACCOUNTS)
missing_accounts = expected_accounts - found_accounts

print(f'Expected accounts: {len(EXPECTED_ACCOUNTS)}')
print(f'Found accounts: {len(found_accounts)}')
print(f'Missing accounts: {len(missing_accounts)}')
if missing_accounts:
    print('\nMissing accounts:')
    print(', '.join(sorted(missing_accounts)))

print('\nTweets per Account:')
print('-' * 50)
print(df.username.value_counts())

# Sample of tweets
print('\nSample of Tweets (first 3):')
print('-' * 50)
print(df[['username', 'timestamp', 'content']].head(3).to_string())
