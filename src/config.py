import os
import logging
from logging.config import fileConfig
from dotenv import load_dotenv, find_dotenv

fileConfig('src/utils/logging_config.ini')
logger = logging.getLogger(__name__)

# Load environment
env_file = find_dotenv()
if env_file:
    load_dotenv(env_file, override=True)

DEFIDIVE_API_URL = "https://api.defidive.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
LANGUAGE = "english"
SENTENCES_COUNT = 10

# Required configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN required in .env file")
if TELEGRAM_BOT_TOKEN:
    logger.info(f"✓ BOT_TOKEN loaded")
else:
    logger.error("⚠️ Warning: DEEPSEEK_API_KEY not set. AI summary will be disabled.")

CHANNEL_ID = os.getenv('CHANNEL_ID')
if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID required in .env file")
else:
    logger.info(f"✓ CHANNEL_ID loaded")
    
# Optional but recommended for synopsis generation
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
if DEEPSEEK_API_KEY:
    logger.info(f"✓ DEEPSEEK_API_KEY loaded")
else:
    logger.error("⚠️ Warning: DEEPSEEK_API_KEY not set. AI summary will be disabled.")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
