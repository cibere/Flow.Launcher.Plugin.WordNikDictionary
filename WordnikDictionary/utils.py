import logging
import logging.handlers

LOG = logging.getLogger(__name__)
__all__ = ("setup_logging",)


def setup_logging() -> None:
    level = logging.DEBUG
    handler = logging.handlers.RotatingFileHandler(
        "wordnik.logs", maxBytes=1000000, encoding="UTF-8"
    )

    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
    )

    logger = logging.getLogger()
    handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(handler)
