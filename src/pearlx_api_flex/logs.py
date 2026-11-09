import logging
import os

from flask import has_app_context, g

LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def init_loggers():
    log_level = LEVELS[os.getenv("LOG_LEVEL", "info").lower()]
    is_colored = bool(int(os.getenv("COLORED_LOGS", 0)))

    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.addFilter(ContextFilter())
    handler.setFormatter(
        ColorFormatter(
            "[%(asctime)s] %(levelname)s %(user_info)s %(module)s: %(message)s",
            is_colored=is_colored,
        )
    )
    logger.addHandler(handler)
    logger.setLevel(log_level)

    logging.getLogger("werkzeug").disabled = True

    for name in (
        "app.access",
        "sqlalchemy",
        "sqlalchemy.engine",
        "sqlalchemy.engine.Engine",
    ):
        logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        handler.addFilter(ContextFilter())
        handler.setFormatter(
            ColorFormatter(
                "[%(asctime)s] %(levelname)s %(user_info)s %(message)s",
                is_colored=is_colored,
            )
        )
        logger.addHandler(handler)
        logger.setLevel(log_level)
        logger.propagate = False


class ColorFormatter(logging.Formatter):
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = [30 + i for i in range(8)]

    RESET_SEQ = "\033[0m"
    COLOR_SEQ_TEMPLATE = "\033[1;%dm"
    BOLD_SEQ = "\033[1m"

    COLORS = {
        logging.DEBUG: COLOR_SEQ_TEMPLATE % BLUE,
        logging.INFO: COLOR_SEQ_TEMPLATE % WHITE,
        logging.WARNING: COLOR_SEQ_TEMPLATE % YELLOW,
        logging.ERROR: COLOR_SEQ_TEMPLATE % RED,
        logging.CRITICAL: COLOR_SEQ_TEMPLATE % MAGENTA,
    }

    def __init__(self, fmt, is_colored=True):
        self.is_colored = is_colored
        logging.Formatter.__init__(self, fmt)

    def format(self, record):
        message = logging.Formatter.format(self, record)
        if not self.is_colored:
            return message
        color = self.COLORS.get(record.levelno)
        if color is None:
            return message
        return f"{color}{message}{self.RESET_SEQ}"


class ContextFilter(logging.Filter):
    def filter(self, log_record):
        log_record.user_info = "-"
        if has_app_context() and getattr(g, "context", None) is not None:
            log_record.user_info = f'{g.context["user_id"]}:{g.context["firstname"]}:{g.context["lastname"]}'
        return True
