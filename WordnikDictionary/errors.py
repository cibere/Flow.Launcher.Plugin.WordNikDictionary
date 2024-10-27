from __future__ import annotations

from .options import Option

__all__ = ("PluginException", "InternalException", "BasePluginException")


class BasePluginException(Exception):
    options: list[Option]

    def __init__(self, text: str, options: list[Option]) -> None:
        super().__init__(text)
        self.options = options


class PluginException(BasePluginException):
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


class InternalException(BasePluginException):
    def __init__(self) -> None:
        opts = [
            Option(score=100, icon="error", title="An internal error has occured."),
            Option(
                score=80,
                icon="github",
                title="Please open a github issue",
                sub="Click this to open github repository",
                callback="open_url",
                params=[
                    "https://github.com/cibere/Flow.Launcher.Plugin.WordNikDictionary"
                ],
            ),
            Option(
                score=79,
                icon="discord",
                title="Or create a thread in our discord server",
                sub="Click on this to open discord invite",
                callback="open_url",
                params=["https://discord.gg/y4STfDvc8j"],
            ),
            Option(
                score=0,
                icon="log_file",
                title="And provide your log file (wordnik.log)",
                sub="Click on this to open plugin folder.",
                callback="open_log_file_folder",
            ),
        ]
        super().__init__("An Interal Error has occured.", opts)

    def final_options(self) -> list[dict]:
        return [opt.to_jsonrpc() for opt in self.options]
