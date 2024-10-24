import json
import os
from typing import Any, Callable

from .dataclass import Dataclass
from .errors import PluginException
from .options import Option

__all__ = ("handle_plugin_exception", "dump_debug", "convert_options")


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


def dump_debug(name: str, data: dict | list) -> None:
    if not os.path.isdir("debug"):
        os.mkdir("debug")

    with open(f"debug/{name}.json", "w") as f:
        json.dump(data, f, indent=4)
