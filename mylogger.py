# encoding=utf-8

import logging
import logging.handlers
from config import *

logger = logging.getLogger('myLogger')
logger.setLevel(logging.DEBUG)
rf_handler = logging.handlers.TimedRotatingFileHandler('result.log', when='midnight', interval=1, backupCount=5)
rf_handler.setFormatter(logging.Formatter("%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s"))
logger.addHandler(rf_handler)
