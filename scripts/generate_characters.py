import os
import base64
import requests
from pathlib import Path

def create_image(prompt: str, filename: str):
    """Generate an image using DALL-E and save it"""
    api_key = os.getenv("Openainew", "")
    if not api_key:
        raise Exception("OpenAI API key not found in environment variables")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
        "model": "dall-e-3",
        "quality": "standard",
        "style": "natural"
    }
    
    response = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers=headers,
        json=data
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to generate image: {response.text}")
        
    image_url = response.json()["data"][0]["url"]
    
    # Download the image
    image_response = requests.get(image_url)
    if image_response.status_code == 200:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            f.write(image_response.content)
    else:
        raise Exception(f"Failed to download image: {image_response.text}")

def main():
    # Create output directories
    base_dir = Path("../frontend/ai_battle_frontend/public/assets/characters")
    openai_dir = base_dir / "openai"
    deepseek_dir = base_dir / "deepseek"
    
    os.makedirs(openai_dir, exist_ok=True)
    os.makedirs(deepseek_dir, exist_ok=True)
    
    # Enhanced character prompts focusing on beauty and sophistication
    openai_prompt = "Beautiful and elegant anime girl with long silver hair and striking blue eyes, wearing a sophisticated white and blue futuristic dress. High-quality digital art style, full body portrait, attractive and refined appearance with gentle expression. Professional and tasteful design with subtle tech-inspired details. Soft lighting, clean background. Elegant pose."
    deepseek_prompt = "Beautiful and graceful anime girl with flowing purple hair and amber eyes, wearing a sleek black and purple tech-inspired outfit. High-quality digital art style, full body portrait, attractive and charismatic appearance with warm expression. Professional and tasteful design with modern accessories. Soft lighting, clean background. Confident pose."
    
    # Generate single expression for each character
    print("Generating OpenAI character...")
    create_image(openai_prompt, str(openai_dir / "openai_normal.png"))
    
    print("Generating DeepSeek character...")
    create_image(deepseek_prompt, str(deepseek_dir / "deepseek_normal.png"))

if __name__ == "__main__":
    main()
