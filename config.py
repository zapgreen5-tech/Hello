"""
Configuration settings for the Zolory Discord Bot
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
BOT_PREFIX = os.getenv("BOT_PREFIX", "!")
BOT_NAME = "Zolory"

# Discord Server Configuration
GUILD_ID = int(os.getenv("GUILD_ID", "0"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///zolory.db")

# Feature Flags
ENABLE_LOGGING = os.getenv("ENABLE_LOGGING", "true").lower() == "true"
ENABLE_MODERATION = os.getenv("ENABLE_MODERATION", "true").lower() == "true"
ENABLE_MUSIC = os.getenv("ENABLE_MUSIC", "true").lower() == "true"

# API Configuration
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))

# Bot Status
ACTIVITY_TYPE = os.getenv("ACTIVITY_TYPE", "watching")
ACTIVITY_MESSAGE = os.getenv("ACTIVITY_MESSAGE", "the server")

# Permissions
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID", "0"))
MODERATOR_ROLE_ID = int(os.getenv("MODERATOR_ROLE_ID", "0"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "zolory.log")

# Rate Limiting
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_CALLS = int(os.getenv("RATE_LIMIT_CALLS", "10"))
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))

# Version
BOT_VERSION = "1.0.0"
