from services.ai_service import CryptoNewsSummarizer
from services.scraping_service import ScrapingService
from config import TELEGRAM_BOT_TOKEN
import logging
from logging.config import fileConfig
import requests

# Initialize logging
fileConfig('src/utils/logging_config.ini')
logger = logging.getLogger(__name__)

CHANNEL_NAME = "-1002693030094" # os.getenv('CHAT_ID')

class BotService:
    def __init__(self, scraping_service: ScrapingService, ai_service: CryptoNewsSummarizer):
        self.scraping_service = scraping_service
        self.ai_service = ai_service

    def start_scraping_article(self):
        """
        Start the scraping process to fetch and summarize cryptocurrency news articles.
        """
        article_list = self.scraping_service.fetch_articles()
        # article_url_list = [article['url'] for article in article_list.get('articles', [])]
        articles = []

        for article in article_list.get('articles', []):
            url = article.get('url')
            blacklisted = ["blog.web3labs.com", "bitcoinist.com", "bitcoinmagazine.com", "bloomberg.com"]
            if any(blacklisted_url in url for blacklisted_url in blacklisted):
                logging.debug(f"⚠️ Skipping blacklisted URL: {url}")
                continue

            try:
                scraped_article = self.scraping_service.scrape_article(url)
            except Exception as e:
                logging.debug(f"⚠️ Skipping Error scraping {url}: {e}")
                continue

            article_data = {
                "url": url,
                "website_name": article.get('website_name'),
                "main_headline": article.get('main_headline'),
                "written_datetime": article.get('written_datetime'),
                "content": self.scraping_service.summarize_article_text(scraped_article.get('text', '')),
                }
            
            # print("\n=== Newspaper3k Output ===")
            # print(json.dumps(article_data, indent=2))
            articles.append(article_data)
        return articles

    def start_summarization(self) -> str:
        """
        Start the summarization process for the fetched articles.
        
        Returns:
            str: The generated summary of the articles.
        """

        try:
            logger.info("🔍 Starting article scraping...")
            articles = self.start_scraping_article()
        except Exception as e:
            logger.error(f"⚠️ Error during scraping: {e}")
            return "Error during scraping articles. Please try again later."
        
        self.ai_service.add_articles(articles)

        try:
            logger.info("📝 Generating summary...")
            summary = self.ai_service.summarize()
            return summary
        except Exception as e:
            logger.error(f"⚠️ Error during summarization: {e}")
            return "Error during summarization. Please try again later."
    
    def format_crypto_summary(json_data: dict) -> str:
        """
        Formats JSON crypto summary into Telegram-friendly message with key points.
        Avoids special characters that need escaping.
        """
        try:
            message = [
                "*CRYPTO MARKET SUMMARY*",
                "",
                json_data["summary"],
                "",
                "*Key Developments:*",
            ]
            
            # Add bullet points for each category
            for category, points in json_data["key_points"].items():
                # Format category name (replace underscores)
                pretty_category = category.replace('_', ' ').title()
                message.append(f"\n*{pretty_category}*")
                for point in points:
                    message.append(f"• {point}")
            
            # Add market implications
            message.extend([
                "\n*Market Implications*",
                *[f"• {implication}" for implication in json_data["market_implications"]]
            ])
            
            return "\n".join(message)
        except Exception as e:
            logger.error(f"⚠️ Error formatting summary: {e}")
            return "Error formatting summary. Please try again later."
    
    def send_to_channel(self, text):
        """Send message to Telegram channel"""
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHANNEL_NAME,
            "text": text,
            "parse_mode": "MarkdownV2"  # For formatting
        }
        
        try:
            logger.info("📤 Sending message to channel...")
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Raise errors for HTTP failures
            logger.info("📧 Message sent to channel successfully")
            return True
        except Exception as e:
            logger.error(f"⚠️ Failed to send to channel: {e.response.text}")
            return False
        
         