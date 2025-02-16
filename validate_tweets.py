import pandas as pd
from datetime import datetime, timedelta

# Read the CSV file
df = pd.read_csv('tweets_20250216_173255.csv')

# Print basic information
print('\nDataset Overview:')
print('-' * 50)
print(f'Total tweets: {len(df)}')
print(f'Unique accounts: {df.username.nunique()}')
print(f'Columns present: {", ".join(df.columns)}')

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Check time window
now = pd.Timestamp.now()
time_diff = now - df['timestamp']
print('\nTimestamp Analysis:')
print('-' * 50)
print(f'Oldest tweet: {df.timestamp.min()}')
print(f'Newest tweet: {df.timestamp.max()}')
print(f'All tweets within 24 hours: {all(time_diff <= pd.Timedelta(days=1))}')

# Check accounts
print('\nTweets per Account:')
print('-' * 50)
print(df.username.value_counts())

# Sample of tweets
print('\nSample of Tweets (first 3):')
print('-' * 50)
print(df[['username', 'timestamp', 'content']].head(3).to_string())
