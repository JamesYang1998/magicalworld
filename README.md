# Twitter Chinese-English Translator

An automatic Twitter plugin that translates Chinese tweets to English using LLM technology.

## Features

- Automatic detection of Chinese tweets
- Real-time translation using OpenAI's GPT models
- Streaming API integration for immediate translations
- Error handling and rate limit management

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export TWITTER_BEARER_TOKEN="your_twitter_bearer_token"
export OPENAI_API_KEY="your_openai_api_key"
```

3. Run the translator:
```bash
python twitter_translator.py
```

## Requirements

- Twitter API Basic tier access ($100/month)
- OpenAI API access
- Python 3.7+

## Note

This plugin uses Twitter's streaming API to monitor for Chinese tweets in real-time and translates them to English using OpenAI's language models.
