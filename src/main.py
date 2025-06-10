import json

from services.scraping_service import  ScrapingService
from services.ai_service import CryptoNewsSummarizer
from services.bot_service import BotService

from config import DEEPSEEK_API_KEY

DEFIDIVE_API_URL = "https://api.defidive.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
LANGUAGE = "english"
SENTENCES_COUNT = 10

if __name__ == "__main__":
    llm_config = {
        "api_key": DEEPSEEK_API_KEY,
    }

    scraper = ScrapingService(
        defidive_api_url=DEFIDIVE_API_URL,
        user_agent=USER_AGENT,
        language=LANGUAGE,
        sentences_count=SENTENCES_COUNT
    )

    # Initialize the summarizer with OpenAI
    summarizer = CryptoNewsSummarizer(
        llm_provider="openai",
        llm_config=llm_config,
        model_name="deepseek-chat"
    )

    bot = BotService(scraping_service=scraper, ai_service=summarizer)
    print("Starting the scraping and summarization process...")
    summary = bot.start_summarization()
    print("Summary generated successfully:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))