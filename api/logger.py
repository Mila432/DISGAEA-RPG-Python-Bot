import logging
import time

logger = logging.getLogger('disgaea_bot')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
fh_formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
handler.setFormatter(fh_formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class Logger:
    @staticmethod
    def log(msg, level):
        logger.log(level, '[%s] %s' % (time.strftime('%H:%M:%S'), msg))

    @staticmethod
    def info(msg):
        Logger.log(msg, logging.INFO)

    @staticmethod
    def error(msg):
        Logger.log(msg, logging.ERROR)

    @staticmethod
    def warn(msg):
        Logger.log(msg, logging.WARN)

    @staticmethod
    def debug(msg):
        Logger.log(msg, logging.DEBUG)
