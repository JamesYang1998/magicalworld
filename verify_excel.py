import pandas as pd
import datetime

def verify_excel_file(filename: str):
    """Verify the contents of the Excel file"""
    print('\nData Verification Results:')
    print('=' * 50)
    
    # Read the Excel file
    df = pd.read_excel(filename)
    
    # Convert timestamp back to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Calculate date ranges
    earliest = df['timestamp'].min()
    latest = df['timestamp'].max()
    cutoff = datetime.datetime.now() - datetime.timedelta(days=90)
    
    # Print verification results
    print(f'Total Posts: {len(df)}')
    print(f'Date Range: {earliest} to {latest}')
    print(f'Posts within 3 months: {(df.timestamp >= cutoff).sum()}/{len(df)}')
    
    print('\nPost Types:')
    print(df['type'].value_counts())
    
    print('\nSample Posts:')
    print(df[['timestamp', 'type', 'content']].head(3))
    
    # Verify data completeness
    print('\nData Completeness:')
    print(f'Missing values: {df.isnull().sum().sum()}')
    
    return {
        'total_posts': len(df),
        'date_range': (earliest, latest),
        'within_3_months': (df.timestamp >= cutoff).sum(),
        'post_types': df['type'].value_counts().to_dict()
    }

if __name__ == "__main__":
    filename = "cz_binance_posts_20250217_022016.xlsx"
    verify_excel_file(filename)
