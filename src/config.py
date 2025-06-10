import os
from dotenv import load_dotenv, find_dotenv

# Load environment
env_file = find_dotenv()
if env_file:
    load_dotenv(env_file, override=True)

# Required configuration
# BOT_TOKEN = os.getenv('BOT_TOKEN')
# if not BOT_TOKEN:
#     raise ValueError("BOT_TOKEN required in .env file")

# Optional but recommended for synopsis generation
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
if not DEEPSEEK_API_KEY:
    print("⚠️ Warning: DEEPSEEK_API_KEY not set. AI summary will be disabled.")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

print(f"✓ BOT_TOKEN loaded")
if DEEPSEEK_API_KEY:
    print(f"✓ Deepseek API key loaded")