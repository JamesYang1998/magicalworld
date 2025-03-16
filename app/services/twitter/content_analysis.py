"""
Twitter Content Analysis Module

This module analyzes Twitter tweets to determine the content focus of a KOL account
using GPT for natural language processing.
"""
import tweepy
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.kol_profile import KOLProfile, ContentFocus
from app.services.twitter.oauth import get_twitter_client
from openai import OpenAI

# OpenAI API key (to be set in environment variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_tweets_with_gpt(tweets: List[Dict]) -> Optional[ContentFocus]:
    """
    Analyze tweets using GPT to determine content focus.
    
    Args:
        tweets: List of tweet data
        
    Returns:
        ContentFocus enum value if successful, None otherwise
    """
    if not OPENAI_API_KEY:
        print("OpenAI API key not configured")
        return None
    
    if not tweets:
        return None
    
    try:
        # Extract tweet text
        tweet_texts = [tweet.get("text", "") for tweet in tweets]
        tweets_str = "\n".join([f"- {text}" for text in tweet_texts])
        
        # Prepare prompt for GPT
        prompt = f"""
        Analyze the following 50 tweets from a Twitter account and categorize the account's primary focus into one of these labels:
        1. 教育 (Education): Educational content, teaching, learning materials, knowledge sharing, academic discussions
        2. 投研 (Investment Research): Investment analysis, market research, trading strategies, cryptocurrency, stocks
        3. 美女 (Beauty/Lifestyle): Fashion, beauty, lifestyle content, modeling, personal aesthetics
        4. 科技 (Technology): Tech news, gadgets, programming, AI, blockchain, software development
        5. 游戏 (Gaming): Video games, gaming culture, esports, game development, streaming
        6. 娱乐 (Entertainment): Celebrity news, movies, music, pop culture, TV shows, memes
        7. 财经 (Finance): Financial news, economics, business, corporate updates, market trends
        8. 其他 (Other): Content that doesn't fit the above categories or spans multiple categories equally

        Tweets:
        {tweets_str}

        Analyze the content, hashtags, and overall theme of these tweets. Provide the most appropriate single label based on the predominant content focus.
        Explain your reasoning briefly in 2-3 sentences, then output only the label name in Chinese.
        """
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a content classifier."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        # Extract label from response
        content = response.choices[0].message.content
        
        # Map the Chinese label to ContentFocus enum
        label_mapping = {
            "教育": ContentFocus.EDUCATION,
            "投研": ContentFocus.INVESTMENT,
            "美女": ContentFocus.BEAUTY,
            "科技": ContentFocus.TECH,
            "游戏": ContentFocus.GAMING,
            "娱乐": ContentFocus.ENTERTAINMENT,
            "财经": ContentFocus.FINANCE,
            "其他": ContentFocus.OTHER,
            "Meme": ContentFocus.MEME
        }
        
        # Find the label in the response
        for label, enum_value in label_mapping.items():
            if label in content:
                return enum_value
        
        # Default to OTHER if no label is found
        return ContentFocus.OTHER
    except Exception as e:
        # Log the error
        print(f"Tweet analysis error: {str(e)}")
        return None

async def analyze_content(profile: KOLProfile, db: Session) -> Optional[ContentFocus]:
    """
    Analyze the content of a Twitter account.
    
    Args:
        profile: KOL profile with Twitter tokens
        db: Database session
        
    Returns:
        ContentFocus enum value if successful, None otherwise
    """
    # Get Twitter client
    client = get_twitter_client(profile, db)
    if not client:
        return None
    
    try:
        # Get user ID
        user = client.get_me()
        user_id = user["data"]["id"]
        
        # Get tweets
        response = client.get_users_tweets(
            user_id,
            max_results=50,
            exclude=["retweets", "replies"],
            tweet_fields=["created_at", "public_metrics"]
        )
        
        tweets = response.get("data", [])
        if not tweets:
            return None
        
        # Analyze tweets
        content_focus = analyze_tweets_with_gpt(tweets)
        if not content_focus:
            return None
        
        # Update profile
        profile.content_label = content_focus
        profile.content_analysis_date = datetime.now()
        db.commit()
        
        return content_focus
    except Exception as e:
        # Log the error
        print(f"Content analysis error: {str(e)}")
        return None

def get_content_label(profile: KOLProfile, db: Session, force_refresh: bool = False) -> Optional[ContentFocus]:
    """
    Get the content label for a KOL profile.
    
    Args:
        profile: KOL profile
        db: Database session
        force_refresh: Whether to force a refresh of the analysis
        
    Returns:
        ContentFocus enum value if available, None otherwise
    """
    # Check if we need to refresh the analysis
    if (force_refresh or 
        profile.content_label is None or 
        profile.content_analysis_date is None or 
        datetime.now() - profile.content_analysis_date > timedelta(days=30)):
        # Schedule background task for analysis
        from app.tasks.twitter_analysis import analyze_content_task
        analyze_content_task.delay(profile.id)
        
    return profile.content_label
