# Twitter Auto-Reply Bot with GPT-4

An AI-powered Twitter bot that automatically generates contextual replies to tweets from specified Twitter list members using GPT-4.

## Features

- Monitors tweets from a specified Twitter list
- Generates contextual replies using GPT-4
- Integrates Strategic Text Sequences (STS) to optimize replies
- Respects rate limits and daily reply quotas
- Handles API errors gracefully
- Configurable monitoring intervals

## Prerequisites

- Python 3.12 or higher
- Twitter API credentials (Developer Account required)
- OpenAI API key

## Installation

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Copy `.env.template` to `.env`:
```bash
cp .env.template .env
```
4. Configure your API credentials in `.env`

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

## STS Integration

The bot can be enhanced with Strategic Text Sequences (STS) to optimize its replies. To use this feature:

1. Generate an STS using llm-rank-optimizer:
```bash
cd path/to/llm-rank-optimizer
python rank_opt.py --results_dir results/my_sts --catalog coffee_machines --target_product_idx 1 --num_iter 100 --random_order --mode self --target_llm llama
```

2. Start the bot with the STS directory:
```bash
python src/run_bot.py path/to/results/my_sts
```

## Usage

1. Start the bot:
```bash
python src/run_bot.py
```

2. For continuous operation with automatic restart:
```bash
python src/run_continuous.py
```

3. The bot will:
   - Monitor the specified Twitter list
   - Generate replies using GPT-4
   - Respect the 3 replies per day limit per user
   - Handle rate limits automatically

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## Customization

- Modify `src/llm.py` to adjust response generation settings
- Update `src/bot.py` to change monitoring behavior
- Edit the list ID in `src/run_bot.py` to monitor a different Twitter list
- Configure STS parameters to optimize different aspects of responses

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
