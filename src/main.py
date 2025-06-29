import logging
from logging.config import fileConfig

fileConfig('src/utils/logging_config.ini')
logger = logging.getLogger(__name__)

from predictor import train_and_predict_data, test_fetch_price, plot_price_with_sma
from services.scraping_service import  ScrapingService
from services.ai_service import CryptoNewsSummarizer
from services.bot_service import BotService
import matplotlib.pyplot as plt

from config import DEEPSEEK_API_KEY, DEFIDIVE_API_URL, USER_AGENT, LANGUAGE, SENTENCES_COUNT


if __name__ == "__main__":
    logger.info("Cron job active. Jobs run every 6 hours...")
    
    logger.info("Job STARTED")
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
        
        cleaned_summary_json = scraper.clean_text(summary)
        bot.send_to_channel(cleaned_summary_json)
    except Exception as e:
        logger.error(f"Failed to send summary: {str(e)}", exc_info=True)
    
    # # === Test predict and plot price data for top tokens ===
    # tokens = test_fetch_price()

    # for token in tokens:
    #     # To get prediction for the next 6 hours
    #     symbol = token.get('token', "")
    #     logger.info(f"Training model for {symbol} prediction...")
        
    #     price_data = token.get('price_data', {})
    #     model, prediction = train_and_predict_data(symbol, price_data)

    #     # To get plot with moving averages
    #     plot_price_with_sma(token['price_data'], title=f"{symbol} Price with Moving Averages")
    #     plt.show()
