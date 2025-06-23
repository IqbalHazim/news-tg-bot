import logging
from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.schedulers.blocking import BlockingScheduler
from logging.config import fileConfig


fileConfig('src/utils/logging_config.ini')
logger = logging.getLogger(__name__)

# from scheduler import schedule_summary
from services.price_service import PriceService
if __name__ == "__main__":
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(schedule_summary, 'interval', hours=6)
    # scheduler.start()

    # logger.info("Scheduler started. Waiting for jobs to run...")
    
    # try:
    #     # Keep the script running to allow the scheduler to run jobs
    #     while True:
    #         pass
    # except (KeyboardInterrupt, SystemExit):
    #     scheduler.shutdown()
    #     logger.info("Scheduler stopped.")
    logger.info("Starting the PriceService to fetch top tokens...")
    price_service = PriceService()
    tokens = price_service.get_top_tokens(limit=3, page="1", sort_by="rank", sort_order="asc")
    logger.info("Top tokens fetched successfully: %s", tokens)
    logger.info("Fetching prices for top tokens...")
    for token in tokens:
        price = price_service.get_price(token)
        logger.info("Price for %s: \n %s", token, price)
