import uvicorn
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting FastAPI server...")
    try:
        # Print environment information
        logger.info("Python version: %s", sys.version)
        logger.info("Current working directory: %s", sys.path[0])

        # Start the server
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,  # Changed port to 8000
            log_level="debug",
            reload=False,
            access_log=True,
            proxy_headers=True,
            forwarded_allow_ips="*"
        )
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        raise
