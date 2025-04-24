import os
import psycopg2
from dotenv import load_dotenv
import logging

# Set up logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_connection():
    load_dotenv()
    db_url = os.getenv('DATABASE_URL')
    
    try:
        logger.info("Attempting to connect to database...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        
        with conn.cursor() as cur:
            # Try a simple query
            cur.execute("SELECT current_database(), current_user, version();")
            db, user, version = cur.fetchone()
            logger.info(f"Connected successfully!")
            logger.info(f"Database: {db}")
            logger.info(f"User: {user}")
            logger.info(f"Version: {version}")
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("Connection closed")

if __name__ == "__main__":
    test_connection() 