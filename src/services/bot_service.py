from services.ai_service import CryptoNewsSummarizer
from services.scraping_service import ScrapingService

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
            # try except here
            url = article.get('url')
            blacklisted = ["blog.web3labs.com", "bitcoinist.com", "bitcoinmagazine.com", "bloomberg.com"]
            if any(blacklisted_url in url for blacklisted_url in blacklisted):
                print(f"Skipping blacklisted URL: {url}")
                continue
            # print(f"Scraping article from: {url}")
            try:
                scraped_article = self.scraping_service.scrape_article(url)
            except Exception as e:
                print(f"⚠️ Skipping Error scraping {url}: {e}")
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
        articles = self.start_scraping_article()
        self.ai_service.add_articles(articles)
        summary = self.ai_service.summarize()
        return summary