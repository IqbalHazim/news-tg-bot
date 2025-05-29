import json

from services.scraping_service import  scrape_article, fetch_articles, scrape_with_bs

if __name__ == "__main__":
    article_list = fetch_articles()
    article_url_list = [article['url'] for article in article_list.get('articles', [])]

    for url in article_url_list:
        blacklisted = ["blog.web3labs.com", "bitcoinist.com", "bitcoinmagazine.com"]
        if any(blacklisted_url in url for blacklisted_url in blacklisted):
            print(f"Skipping blacklisted URL: {url}")
            continue
        print(f"Scraping article from: {url}")
        article_data = scrape_article(url)
        print("\n=== Newspaper3k Output ===")
        print(json.dumps(article_data, indent=2))

        with open("scraped_article.json", "w") as f:
            json.dump(article_data, f, indent=2)