from setuptools import setup, find_packages

setup(
    name="magicalworld",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "tweepy>=4.14.0",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "pytest>=8.0.0",
        "flake8>=7.0.0"
    ],
)
