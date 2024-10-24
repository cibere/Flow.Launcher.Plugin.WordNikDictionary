from __future__ import annotations
from typing import Any

__all__ = ("Option",)


class Option:
    def __init__(
        self,
        *,
        title: str,
        sub: str = "",
        callback: str | None = None,
        params: list[str] = [],
        context_data: list[Option] = [],
    ):
        self.title = title
        self.sub = sub
        self.callback = callback
        self.params = params
        self.context_data = context_data

    def to_jsonrpc(self) -> dict:
        data: dict[str, Any] = {
            "Title": self.title,
            "SubTitle": self.sub,
            "IcoPath": "Images/app.png",
            "ContextData": [opt.to_jsonrpc() for opt in self.context_data],
        }
        if self.callback:
            data["JsonRPCAction"] = {"method": self.callback, "parameters": self.params}
        return data

    @classmethod
    def url(cls: type[Option], name: str, url: str) -> Option:
        return Option(title=f"Open {name}", sub=url, callback="open_url", params=[url])

    @classmethod
    def wnf(cls: type[Option]) -> Option:
        return cls(title="Word not found")
