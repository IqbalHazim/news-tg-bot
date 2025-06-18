import logging
from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.schedulers.blocking import BlockingScheduler
from logging.config import fileConfig
from scheduler import schedule_summary

fileConfig('src/utils/logging_config.ini')
logger = logging.getLogger(__name__)


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