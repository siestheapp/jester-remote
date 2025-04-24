import os
import psycopg2
from dotenv import load_dotenv
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_migration(migration_file, direction='up'):
    """Run the SQL migration in the specified direction."""
    load_dotenv()

    # Get database connection details from environment variables
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")

    logger.info(f"Attempting to connect to database with URL: {db_url.split('@')[1]}")  # Log URL without password
    
    try:
        # Connect to the database with autocommit for pgbouncer compatibility
        conn = psycopg2.connect(db_url)
        conn.autocommit = True  # Required for pgbouncer
        logger.info("Successfully connected to database")
        
        # Read the migration file
        migration_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data',
            'migrations',
            migration_file
        )
        
        logger.info(f"Reading migration file: {migration_path}")
        with open(migration_path, 'r') as f:
            sql_content = f.read()

        # Split the content into up and down migrations
        up_migration = sql_content.split('-- Down Migration')[0]
        down_migration = sql_content.split('-- Down Migration')[1]

        # Execute the appropriate migration
        with conn.cursor() as cur:
            if direction == 'up':
                logger.info(f"Running UP migration for {migration_file}...")
                # Split and execute statements individually since we're in autocommit mode
                statements = [s.strip() for s in up_migration.split(';') if s.strip()]
                for statement in statements:
                    if statement.strip().upper().startswith('BEGIN'):
                        continue  # Skip BEGIN statements as we're in autocommit mode
                    if statement.strip().upper() == 'COMMIT':
                        continue  # Skip COMMIT statements as we're in autocommit mode
                    logger.info(f"Executing statement: {statement[:100]}...")  # Log first 100 chars
                    cur.execute(statement)
            else:
                logger.info(f"Running DOWN migration for {migration_file}...")
                # Split and execute statements individually since we're in autocommit mode
                statements = [s.strip() for s in down_migration.split(';') if s.strip()]
                for statement in statements:
                    if statement.strip().upper().startswith('BEGIN'):
                        continue  # Skip BEGIN statements as we're in autocommit mode
                    if statement.strip().upper() == 'COMMIT':
                        continue  # Skip COMMIT statements as we're in autocommit mode
                    logger.info(f"Executing statement: {statement[:100]}...")  # Log first 100 chars
                    cur.execute(statement)

        logger.info(f"Migration {direction} completed successfully!")

    except psycopg2.OperationalError as e:
        logger.error(f"Database connection error: {str(e)}")
        raise
    except psycopg2.Error as e:
        logger.error(f"PostgreSQL error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise

    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: python run_migration.py <migration_file> [direction]")
        sys.exit(1)
        
    migration_file = sys.argv[1]
    direction = sys.argv[2] if len(sys.argv) > 2 else 'up'
    run_migration(migration_file, direction) 