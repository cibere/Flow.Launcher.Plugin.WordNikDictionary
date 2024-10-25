import logging
import logging.handlers
from typing import Any, Callable

from .dataclass import Dataclass
from .errors import PluginException
from .options import Option

__all__ = ("handle_plugin_exception", "convert_options", "setup_logging")


def handle_plugin_exception(func: Callable[..., Any]) -> Callable[..., Any]:
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PluginException as e:
            return e.options

    return inner


def convert_options(func: Callable[..., Any]) -> Callable[..., Any]:
    def inner(*args, **kwargs):
        try:
            options = func(*args, **kwargs)
        except PluginException as e:
            options = e.options
        final = []
        for opt in options:
            if isinstance(opt, Dataclass):
                opt = opt.to_option()
            if isinstance(opt, Option):
                final.append(opt.to_jsonrpc())
            else:
                raise RuntimeError(f"Unknown option returned: {opt!r}")
        return final

    return inner


def setup_logging() -> None:
    level = logging.DEBUG
    handler = logging.handlers.RotatingFileHandler("wordnik.logs", maxBytes=1000000)
    
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
    )

    logger = logging.getLogger()
    handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(handler)
