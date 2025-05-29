import requests
from bs4 import BeautifulSoup
from newspaper import Article, Config
import json

DEFIDIVE_API_URL = "https://api.defidive.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

config = Config()
config.browser_user_agent = USER_AGENT
config.request_timeout = 10

def fetch_articles():
    """Fetch articles from a predefined URL."""
    news_url = f"{DEFIDIVE_API_URL}/news/article/latest?numArticlesPerSource=5"
    try:
        response = requests.get(news_url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Request Error: {e}")
        return None
    

def scrape_article(url):
    """Scrape article text using Newspaper3k and BeautifulSoup."""
    try:
        article = Article(url, config=config)
        article.download()
        article.parse()
        
        return {
            "title": article.title,
            "text": article.text,
            "authors": article.authors,
            "publish_date": str(article.publish_date),
            "top_image": article.top_image,
            "keywords": article.keywords,
            "summary": article.summary
        }
    except Exception as e:
        print(f"⚠️ Newspaper3k Error: {e}")
        return None
    
def scrape_with_bs(url, css_selector):
    """Scrape specific content using BeautifulSoup."""
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise HTTP errors
        
        soup = BeautifulSoup(response.text, 'html.parser')
        selected_content = soup.select(css_selector)
        
        # Extract text from all selected elements
        return " ".join([elem.get_text(strip=True) for elem in selected_content])
    except Exception as e:
        print(f"⚠️ BeautifulSoup Error: {e}")
        return None