from __future__ import annotations

from flogin import Result

__all__ = ("PluginException", "WordNotFound")


class PluginException(Exception):
    def __init__(self, msg: str, res: Result | None = None):
        super().__init__(msg)
        self.result = res


class WordNotFound(Exception):
    def __init__(self, word: str):
        super().__init__(f"Word not found: {word!r}")
        self.word = word


class InternalException(PluginException):
    def __init__(self) -> None:
        super().__init__("An Interal Error has occured.")
