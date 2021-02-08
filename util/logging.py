import http
import logging
import os


def initLogging(level=logging.DEBUG):
    if not os.path.exists('logs'):
        os.makedirs('logs')
    # noinspection PyArgumentList
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/debug.log"),
            logging.StreamHandler()
        ]
    )

    if level == logging.DEBUG:
        """Logging wrapper for HTTP calls, set to DEBUG by default"""
        httpclient_logger = logging.getLogger("http.client")

        def httpclient_log(*args):
            httpclient_logger.log(level, " ".join(args))

        # mask the print() built-in in the http.client module to use
        # logging instead
        http.client.print = httpclient_log
        # enable debugging
        http.client.HTTPConnection.debuglevel = 1
