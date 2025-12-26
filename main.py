"""
Zolory Bot - Main Initialization Module
Created: 2025-12-26
Description: Main bot initialization and setup for Zolory
"""

import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ZoloryBot:
    """Main bot class for Zolory initialization and management"""
    
    def __init__(self):
        """Initialize the Zolory bot"""
        logger.info("Initializing Zolory Bot...")
        self.start_time = datetime.utcnow()
        self.version = "1.0.0"
        self.status = "initialized"
        
    def startup(self):
        """Startup sequence for the bot"""
        try:
            logger.info(f"Starting Zolory Bot v{self.version}")
            self.status = "running"
            logger.info("Bot startup completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error during bot startup: {e}")
            self.status = "error"
            return False
    
    def shutdown(self):
        """Shutdown sequence for the bot"""
        logger.info("Shutting down Zolory Bot...")
        self.status = "stopped"
        logger.info("Bot shutdown completed")
    
    def get_status(self):
        """Get current bot status"""
        uptime = datetime.utcnow() - self.start_time
        return {
            "status": self.status,
            "version": self.version,
            "uptime": str(uptime),
            "started_at": self.start_time.isoformat()
        }


def main():
    """Main entry point for Zolory Bot"""
    try:
        # Initialize bot
        bot = ZoloryBot()
        
        # Startup bot
        if bot.startup():
            logger.info(f"Bot status: {bot.get_status()}")
            
            # Keep bot running
            logger.info("Zolory Bot is now running...")
            
            # Graceful shutdown
            bot.shutdown()
            sys.exit(0)
        else:
            logger.error("Failed to start bot")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        bot.shutdown()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
