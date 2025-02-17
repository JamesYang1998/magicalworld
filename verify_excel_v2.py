import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

def verify_excel_file(filename: str):
    """Verify the contents of the Excel file with detailed analysis"""
    print('\nData Verification Results:')
    print('=' * 50)
    
    # Read the Excel file
    df = pd.read_excel(filename)
    
    # Convert timestamp back to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Calculate date ranges
    earliest = df['timestamp'].min()
    latest = df['timestamp'].max()
    date_range = (latest - earliest).days
    
    # Print basic statistics
    print(f'Total Posts: {len(df)}')
    print(f'\nDate Range:')
    print(f'Earliest: {earliest}')
    print(f'Latest: {latest}')
    print(f'Total Days: {date_range}')
    
    # Content type distribution
    print('\nContent Type Distribution:')
    type_dist = df['type'].value_counts()
    print(type_dist)
    
    # Engagement statistics
    print('\nEngagement Statistics:')
    for col in ['replies', 'retweets', 'likes', 'quotes']:
        values = []
        for val in df[col]:
            try:
                if 'M' in val:
                    values.append(float(val.replace('M', '')) * 1000000)
                elif 'K' in val:
                    values.append(float(val.replace('K', '')) * 1000)
                else:
                    values.append(float(val))
            except:
                values.append(0)
        
        avg_val = sum(values) / len(values)
        if avg_val >= 1000000:
            avg_str = f"{avg_val/1000000:.1f}M"
        elif avg_val >= 1000:
            avg_str = f"{avg_val/1000:.1f}K"
        else:
            avg_str = f"{int(avg_val)}"
        
        print(f'Average {col}: {avg_str}')
    
    # Posts per day
    df['date'] = df['timestamp'].dt.date
    posts_per_day = df.groupby('date').size()
    print(f'\nPosts per Day:')
    print(f'Average: {posts_per_day.mean():.1f}')
    print(f'Maximum: {posts_per_day.max()}')
    print(f'Minimum: {posts_per_day.min()}')
    
    # Data completeness
    print('\nData Completeness:')
    print(f'Missing values: {df.isnull().sum().sum()}')
    
    # Original authors for retweets
    retweets = df[df['type'] == 'Retweet']
    if not retweets.empty:
        print('\nRetweeted Authors:')
        print(retweets['original_author'].value_counts().head())
    
    return {
        'total_posts': len(df),
        'date_range': (earliest, latest),
        'type_distribution': type_dist.to_dict(),
        'posts_per_day': {
            'average': posts_per_day.mean(),
            'maximum': posts_per_day.max(),
            'minimum': posts_per_day.min()
        }
    }

if __name__ == "__main__":
    filename = "cz_binance_posts_complete_20250217_025532.xlsx"
    verify_excel_file(filename)
