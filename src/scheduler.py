import logging
from apscheduler.schedulers.background import BackgroundScheduler
from logging.config import fileConfig
from services.scraping_service import  ScrapingService
from services.ai_service import CryptoNewsSummarizer
from services.bot_service import BotService

from config import DEEPSEEK_API_KEY, DEFIDIVE_API_URL, USER_AGENT, LANGUAGE, SENTENCES_COUNT

fileConfig('src/utils/logging_config.ini')
logger = logging.getLogger(__name__)

def schedule_summary():
    logger.info("Scheduler job STARTED")
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
    logger.info("Starting the scraping and summarization process...")

    try:
        summary = bot.start_summarization()
        logger.info("Summary generated successfully!")
        
        cleaned_summary_json = summary.replace("/ ", "").replace("/n ", "").strip()
        bot.send_to_channel(cleaned_summary_json)
    except Exception as e:
        logger.error(f"Failed to send summary: {str(e)}", exc_info=True)
