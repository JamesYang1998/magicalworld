# Twitter Auto-Reply Bot with GPT-4

An AI-powered Twitter bot that automatically generates contextual replies to tweets from specified Twitter list members using GPT-4.

Draft PR verification test - Adding this line to create a difference between branches.

Draft PR verification test.

## Features

- Monitors tweets from a specified Twitter list
- Generates contextual replies using GPT-4
- Respects rate limits and daily reply quotas
- Handles API errors gracefully
- Configurable monitoring intervals

## Prerequisites

- Python 3.12 or higher
- Twitter API credentials (Developer Account required)
- OpenAI API key

## Installation

1. Install Python 3.12 and Git from their official websites:
   - Python: https://www.python.org/downloads/
   - Git: https://git-scm.com/downloads

2. Clone the repository:
   ```bash
   # If you encounter HTTP2 errors, use this command:
   git -c http.version=1.1 clone https://github.com/JamesYang1998/magicalworld.git
   cd magicalworld
   ```

3. Install dependencies:
   ```bash
   # If you encounter SSL certificate errors, use this command:
   pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # On Windows:
   copy .env.template .env
   
   # On Linux/Mac:
   cp .env.template .env
   ```

5. Configure your API credentials in `.env`

## Configuration

Edit the `.env` file with your API credentials:

```plaintext
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

1. Start the bot:
```bash
python3 src/run_bot.py
```

2. The bot will:
   - Monitor the specified Twitter list
   - Generate replies using GPT-4
   - Respect the 3 replies per day limit per user
   - Handle rate limits automatically

## Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

## Customization

- Modify `src/llm.py` to adjust response generation settings
- Update `src/bot.py` to change monitoring behavior
- Edit the list ID in `src/run_bot.py` to monitor a different Twitter list

## Error Handling

The bot includes comprehensive error handling for:
- Twitter API rate limits
- Network issues
- API authentication errors
- Response generation failures

## Limitations

- Maximum 3 replies per user per day
- Respects Twitter's rate limits
- Requires valid API credentials
