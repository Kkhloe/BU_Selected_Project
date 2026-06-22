import sys
from loguru import logger

def setup_logger():
    logger.remove()
    
    # Console logger - clean format
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    # JSON file logger - using loguru's built-in serialization
    logger.add(
        "logs/app.json.log",
        serialize=True,
        level="INFO",
        rotation="10 MB"
    )

setup_logger()
