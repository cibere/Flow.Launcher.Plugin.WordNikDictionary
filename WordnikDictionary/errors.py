from __future__ import annotations
from .options import Option

__all__ = ("PluginException",)


class PluginException(Exception):
    options: list[Option]

    def __init__(self, text: str, options: list[Option]) -> None:
        super().__init__(text)
        self.options = options

    @classmethod
    def create(
        cls: type[PluginException],
        text: str,
        sub: str = "",
        url: str | None = None,
        **kwargs,
    ) -> PluginException:
        if url is not None:
            kwargs["callback"] = "open_url"
            kwargs["params"] = [url]

        return cls(text, [Option(title=text, sub=sub, **kwargs)])

    @classmethod
    def wnf(cls: type[PluginException]) -> PluginException:
        opt = Option.wnf()
        return cls(opt.title, [opt])