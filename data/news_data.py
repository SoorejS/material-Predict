import requests
import os
import logging
from dotenv import load_dotenv

# Load environment variables (API keys)
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your actual NewsAPI key
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "YOUR_NEWS_API_KEY_HERE")

def fetch_news(query: str, limit: int = 10) -> list:
    """
    Fetches the latest news articles for a given query (e.g., 'Gold futures') using NewsAPI.
    :param query: Query string to search for news
    :param limit: Number of top stories to fetch
    :return: List of headlines + descriptions
    """
    if NEWS_API_KEY == "YOUR_NEWS_API_KEY_HERE":
        logger.warning("No NewsAPI key found. Using mock sentiment for now.")
        return [
            f"Mock headline for {query}: Predicted growth due to market demand.",
            f"Mock headline for {query}: Concerns over central bank rate hikes.",
            f"Mock headline for {query}: Prices stable amid holiday season trading."
        ]

    try:
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()  # Check for errors (e.g., 401 Unauthorized)
        
        data = response.json()
        articles = data.get("articles", [])
        
        # Combine title and description for analysis
        summaries = [
            (a.get("title", "") + " " + (a.get("description", "") or ""))
            for a in articles[:limit]
        ]
        
        logger.info(f"Successfully fetched {len(summaries)} news articles for {query}")
        return summaries
    except Exception as e:
        logger.error(f"Error fetching news for {query}: {e}")
        return []

if __name__ == "__main__":
    # Test fetch
    news = fetch_news("gold")
    for story in news[:3]:
        print(f"- {story[:100]}...")
