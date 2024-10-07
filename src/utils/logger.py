from loguru import logger
import sys
from pathlib import Path

def setup_logger():
    """
    Setup logging configuration.
    """
    logger.remove()
    log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | <cyan>{name}</cyan> | <cyan>{function}</cyan> | <level>{message}</level>"
    logger.add(sys.stdout, format=log_format, level="INFO")
    Path("logs").mkdir(parents=True, exist_ok=True)
    logger.add("logs/logfile.log", rotation="500 MB", level="DEBUG", format=log_format)
    logger.info("Logger initialized")
