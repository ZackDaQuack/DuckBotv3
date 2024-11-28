"""

File: duckLog.py
Author: ZackDaQuack
Last Edited: 11/27/2024

Info:

Uh it does what you think. Creates a logger, and saves files. Pretty boring.

"""

import logging
import colorlog
import configparser
from datetime import datetime

config = configparser.ConfigParser()
config.read('config.ini')

timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_file = f"logs/duckBot_session_{timestamp}.log"

file_handler = logging.FileHandler(filename=log_file, mode='w', encoding='utf-8')
console_handler = colorlog.StreamHandler()

console_handler.setFormatter(
    colorlog.ColoredFormatter(
        '%(log_color)s[%(asctime)s] [%(levelname)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    )
)

file_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
)

logger = colorlog.getLogger('quack_logger')
logger.addHandler(file_handler)
logger.addHandler(console_handler)

level = int(config.get("GENERAL", "log_level"))
if level == 1:
    logger.setLevel(logging.DEBUG)
elif level == 2:
    logger.setLevel(logging.INFO)
elif level == 3:
    logger.setLevel(logging.WARNING)
elif level == 4:
    logger.setLevel(logging.ERROR)
elif level == 5:
    logger.setLevel(logging.CRITICAL)
