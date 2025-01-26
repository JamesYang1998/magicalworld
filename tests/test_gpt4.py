#!/usr/bin/env python3

import os
from openai import OpenAI


def test_gpt4_access():
    """
    Test GPT-4 access with the current OpenAI API key
    """
    try:
        print("Initializing OpenAI client with provided key...")
        client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        
        print("\nTesting GPT-4 access...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a friendly Twitter bot. "
                        "Generate an interesting fact or thought in English."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        "Generate a brief, engaging tweet about an interesting fact "
                        "(must be under 280 characters)."
                    )
                }
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        if response and response.choices:
            content = response.choices[0].message.content.strip()
            print("\nSuccessfully generated content using GPT-4:")
            print(f"Content: {content}")
            print("\nGPT-4 access verified successfully!")
            return True
            
    except Exception as e:
        print(f"Error testing GPT-4 access: {e}")
        print(f"Error type: {type(e)}")
        return False

if __name__ == "__main__":
    test_gpt4_access()
