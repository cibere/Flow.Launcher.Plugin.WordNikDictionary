from typing import Callable, Any
from .errors import PluginException

__all__ = ("handle_plugin_exception",)


def handle_plugin_exception(func: Callable[..., Any]) -> Callable[..., Any]:
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PluginException as e:
            return e.options

    return inner
