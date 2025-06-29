import logging
from apscheduler.schedulers.background import BackgroundScheduler
from logging.config import fileConfig
import matplotlib.pyplot as plt

fileConfig('src/utils/logging_config.ini')
logger = logging.getLogger(__name__)

from scheduler import schedule_summary
from predictor import train_and_predict_data, test_fetch_price, plot_price_with_sma

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(schedule_summary, 'interval', hours=6)
    scheduler.start()

    logger.info("Scheduler started. Waiting for jobs to run...")
    
    try:
        # Keep the script running to allow the scheduler to run jobs
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler stopped.")

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
