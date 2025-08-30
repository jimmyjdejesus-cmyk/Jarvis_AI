# logger_config.py
import logging
import sys

def setup_logger():
    # Create a logger
    logger = logging.getLogger('J.A.R.V.I.S.')
    logger.setLevel(logging.INFO)

    # Create a file handler which logs even debug messages
    fh = logging.FileHandler('jarvis_local.log', mode='w')
    fh.setLevel(logging.INFO)

    # Create a console handler with a higher log level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Add the handlers to the logger
    # Avoid adding handlers if they already exist
    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger

# Create a logger instance to be imported by other modules
log = setup_logger()