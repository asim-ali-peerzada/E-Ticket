import os
import django
import time
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Ticket.settings')
django.setup()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the job to run
def createtrips():
    logger.info("Running scheduled command: create_trips")
    call_command('create_trips')
    logger.info("Scheduled command completed: create_trips")

# Set up the scheduler
scheduler = BackgroundScheduler()

# Schedule the job to run every night at 12 AM
scheduler.add_job(createtrips, 'cron', hour=0, minute=27)

# Start the scheduler
if __name__ == "__main__":
    logger.info("Starting scheduler...")
    scheduler.start()
    
    try:
        while True:
            logger.info("Scheduler is running. Sleeping for 24 hours.")
            time.sleep(86400)  # Sleep for 24 hours
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler shutdown.")
