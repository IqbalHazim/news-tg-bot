import json

from services.scraping_service import  scrape_article, fetch_articles, summarize_article_text
from services.ai_service import CryptoNewsSummarizer

if __name__ == "__main__":
    article_list = fetch_articles()
    # article_url_list = [article['url'] for article in article_list.get('articles', [])]
    articles = []

    for article in article_list.get('articles', []):
        # try except here
        url = article.get('url')
        blacklisted = ["blog.web3labs.com", "bitcoinist.com", "bitcoinmagazine.com", "bloomberg.com"]
        if any(blacklisted_url in url for blacklisted_url in blacklisted):
            print(f"Skipping blacklisted URL: {url}")
            continue
        print(f"Scraping article from: {url}")
        scraped_article = scrape_article(url)
        article_data = {
            "url": url,
            "website_name": article.get('website_name'),
            "main_headline": article.get('main_headline'),
            "written_datetime": article.get('written_datetime'),
            "content": summarize_article_text(scraped_article.get('text', '')),
            }
        
        print("\n=== Newspaper3k Output ===")
        print(json.dumps(article_data, indent=2))
        articles.append(article_data)

    llm_config = {
        "api_key": "sk-f245ee6525f9490eb5f3683b6724daeb",  # Replace with your actual API key
    }

    # Initialize the summarizer with OpenAI
    summarizer = CryptoNewsSummarizer(
        llm_provider="openai",
        llm_config=llm_config,
        model_name="deepseek-chat"
    )

    summarizer.add_articles(articles)
    summary = summarizer.summarize()
    print("\n=== Summary Output ===")
    print(summary)