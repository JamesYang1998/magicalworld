from PIL import Image
import os
from pathlib import Path

def optimize_images(directory):
    """Resize and optimize images in the given directory."""
    for filename in os.listdir(directory):
        if filename.endswith(".png"):
            filepath = os.path.join(directory, filename)
            with Image.open(filepath) as img:
                # Resize to 512x512
                img = img.resize((512, 512), Image.Resampling.LANCZOS)
                # Save with optimization
                img.save(filepath, "PNG", optimize=True, quality=85)
                print(f"Optimized {filename}")

def main():
    base_dir = Path("../frontend/ai_battle_frontend/public/assets/characters")
    optimize_images(base_dir / "openai")
    optimize_images(base_dir / "deepseek")

if __name__ == "__main__":
    main()
