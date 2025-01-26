"""Mock data for testing the Twitter bot"""

MOCK_TWEETS = [
    {
        'id': '1',
        'text': 'This is a test tweet #1',
        'author_id': '101',
        'referenced_tweets': None
    },
    {
        'id': '2',
        'text': 'This is a test tweet #2',
        'author_id': '102',
        'referenced_tweets': None
    },
    {
        'id': '3',
        'text': 'This is a retweet',
        'author_id': '103',
        'referenced_tweets': [{'type': 'retweeted', 'id': '1'}]
    }
]

MOCK_USERS = {
    '101': {
        'id': '101',
        'username': 'testuser1'
    },
    '102': {
        'id': '102',
        'username': 'testuser2'
    },
    '103': {
        'id': '103',
        'username': 'testuser3'
    }
}
