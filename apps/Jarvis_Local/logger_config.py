# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



import logging
import sys

def setup_logger():
    logger = logging.getLogger('J.A.R.V.I.S.')
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        # File Handler
        fh = logging.FileHandler('adaptivemind_local.log', mode='w')
        fh.setLevel(logging.INFO)
        # Console Handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # Add Handlers
        logger.addHandler(fh)
        logger.addHandler(ch)
    return logger

log = setup_logger()