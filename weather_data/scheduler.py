import schedule
import time
import logging
from datetime import datetime
from weather_extractor import UAEWeatherExtractor
from weather_api_backup import WeatherAPIBackup

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weather_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WeatherDataScheduler:
    """
    Scheduler for automated weather data collection
    """
    
    def __init__(self, api_key=None):
        self.extractor = UAEWeatherExtractor()
        self.api_backup = WeatherAPIBackup(api_key) if api_key else None
    
    def scheduled_wikipedia_extraction(self):
        """Run Wikipedia weather data extraction on schedule"""
        try:
            logger.info("🕐 Starting scheduled Wikipedia extraction...")
            success_count, failed_cities = self.extractor.extract_all_cities()
            
            logger.info(f"✅ Scheduled extraction completed: {success_count}/7 cities successful")
            
            if failed_cities:
                logger.warning(f"❌ Failed cities in scheduled run: {failed_cities}")
                
        except Exception as e:
            logger.error(f"❌ Scheduled extraction failed: {e}")
    
    def scheduled_api_collection(self):
        """Run API weather data collection on schedule"""
        if not self.api_backup:
            logger.warning("⚠️  API backup not configured, skipping API collection")
            return
            
        try:
            logger.info("🕐 Starting scheduled API collection...")
            success_count = self.api_backup.collect_all_current_weather()
            logger.info(f"✅ Scheduled API collection completed: {success_count}/7 cities successful")
            
        except Exception as e:
            logger.error(f"❌ Scheduled API collection failed: {e}")
    
    def run_scheduler(self):
        """Start the scheduler with predefined intervals"""
        
        # Schedule Wikipedia extraction
        # Daily at 9 AM for comprehensive data
        schedule.every().day.at("09:00").do(self.scheduled_wikipedia_extraction)
        
        # Weekly on Sundays at 6 AM for fresh data
        schedule.every().sunday.at("06:00").do(self.scheduled_wikipedia_extraction)
        
        # Schedule API collection (if available)
        if self.api_backup:
            # Every 6 hours for current weather updates
            schedule.every(6).hours.do(self.scheduled_api_collection)
            
            # Every day at 12 PM for midday current weather
            schedule.every().day.at("12:00").do(self.scheduled_api_collection)
        
        logger.info("🚀 Weather data scheduler started with the following schedule:")
        logger.info("📅 Wikipedia extraction: Daily at 9 AM, Weekly on Sunday at 6 AM")
        
        if self.api_backup:
            logger.info("🌐 API collection: Every 6 hours, Daily at 12 PM")
        else:
            logger.info("⚠️  API collection: Disabled (no API key provided)")
        
        logger.info("Press Ctrl+C to stop the scheduler")
        
        try:
            # Run Wikipedia extraction once immediately
            logger.info("🔄 Running initial Wikipedia extraction...")
            self.scheduled_wikipedia_extraction()
            
            # Run API collection once immediately if available
            if self.api_backup:
                logger.info("🔄 Running initial API collection...")
                self.scheduled_api_collection()
            
            # Keep running scheduled tasks
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("⏹️  Scheduler stopped by user")
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")

def run_manual_extraction():
    """Run manual extraction without scheduling"""
    print("🚀 Running manual weather data extraction...")
    
    extractor = UAEWeatherExtractor()
    success_count, failed_cities = extractor.extract_all_cities()
    
    print(f"\n✅ Manual extraction completed: {success_count}/7 cities successful")
    
    if failed_cities:
        print(f"❌ Failed cities: {failed_cities}")
    
    # Display results
    extractor.display_summary()

if __name__ == "__main__":
    import sys
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "manual":
        # Run manual extraction
        run_manual_extraction()
    else:
        # Run scheduler
        # Optional: Add your OpenWeatherMap API key here
        API_KEY = None  # Replace with your actual API key
        
        scheduler = WeatherDataScheduler(api_key=API_KEY)
        scheduler.run_scheduler()