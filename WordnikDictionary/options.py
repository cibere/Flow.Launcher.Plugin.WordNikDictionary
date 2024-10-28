from __future__ import annotations

from typing import Any

__all__ = ("Option",)


class Option:
    def __init__(
        self,
        *,
        title: str,
        sub: Any = "",
        callback: str | None = None,
        params: list[Any] = [],
        context_data: list[Option] = [],
        hide_after_callback: bool = True,
        score: int = 0,
        icon: str = "app",
    ):
        self.title = title
        self.icon_name = icon
        self.sub = sub
        self.callback = callback
        self.params = params
        self.score = score
        self.context_data = context_data
        self.hide_after_callback = (
            False if callback == "change_query" else hide_after_callback
        )

    @property
    def icon(self) -> str:
        return f"Images/{self.icon_name}.png"

    @icon.setter
    def icon(self, name: str) -> None:
        self.icon_name = name

    def to_jsonrpc(self) -> dict:
        data: dict[str, Any] = {
            "Title": self.title,
            "SubTitle": str(self.sub),
            "IcoPath": self.icon,
            "ContextData": [opt.to_jsonrpc() for opt in self.context_data],
            "score": self.score,
        }
        if self.callback:
            data["JsonRPCAction"] = {
                "method": self.callback,
                "parameters": self.params,
                "dontHideAfterAction": not self.hide_after_callback,
            }
        return data

    @classmethod
    def url(cls: type[Option], name: str, url: str) -> Option:
        return Option(title=f"Open {name}", sub=url, callback="open_url", params=[url])

    @classmethod
    def wnf(cls: type[Option]) -> Option:
        return cls(title="Word not found", icon="error")
