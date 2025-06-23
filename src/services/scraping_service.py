import requests
from bs4 import BeautifulSoup
from newspaper import Article, Config
from sumy.summarizers.luhn import LuhnSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.utils import get_stop_words
from sumy.parsers.plaintext import PlaintextParser
import logging

import nltk
nltk.download('punkt_tab')

logger = logging.getLogger(__name__)

class ScrapingService:
    def __init__(self, defidive_api_url: str, user_agent: str, language: str, sentences_count: int):
        """Initialize the scraping service."""
        self.defidive_api_url = defidive_api_url
        self.user_agent = user_agent
        self.language = language
        self.sentences_count = sentences_count

    def fetch_articles(self):
        """Fetch articles from a predefined URL."""
        news_url = f"{self.defidive_api_url}/news/article/latest?numArticlesPerSource=5"
        try:
            response = requests.get(news_url)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"⚠️ Request Error: {e}")
            return None
        

    def scrape_article(self, url) -> dict:
        """Scrape article text using Newspaper3k and BeautifulSoup."""
        try:
            config = Config()
            config.browser_user_agent = self.user_agent
            config.request_timeout = 10
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
            logger.debug(f"⚠️ Newspaper3k Error: {e}")
            raise e
        
    def scrape_with_bs(self, url, css_selector):
        """Scrape specific content using BeautifulSoup."""
        try:
            headers = {'User-Agent': self.user_agent}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise HTTP errors
            
            soup = BeautifulSoup(response.text, 'html.parser')
            selected_content = soup.select(css_selector)
            
            # Extract text from all selected elements
            return " ".join([elem.get_text(strip=True) for elem in selected_content])
        except Exception as e:
            logger.debug(f"⚠️ BeautifulSoup Error: {e}")
            return None

    def summarize_article_text(self, article_text: str) -> str:
        """Summarize article text using a simple heuristic."""
        try:
            parser = PlaintextParser.from_string(article_text, Tokenizer(self.language))
            stemmer = Stemmer(self.language)
            summarizer = Summarizer(stemmer)
            summarizer.stop_words = get_stop_words(self.language)
            summarized_text = " ".join(str(sentence) for sentence in summarizer(parser.document, self.sentences_count))
            return summarized_text.strip() if summarized_text else "No summary available."
        except Exception as e:
            logger.debug(f"⚠️ Summarization Error: {e}")
            raise e
