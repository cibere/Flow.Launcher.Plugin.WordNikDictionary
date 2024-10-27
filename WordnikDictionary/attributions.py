from __future__ import annotations

__all__ = ("Attribution",)


class Attribution:
    def __init__(self, text: str | None, url: str | None) -> None:
        self.text = text or ""
        self.url = url

    @classmethod
    def from_json(cls: type[Attribution], data: dict) -> Attribution:
        return cls(data["attributionText"], data["attributionUrl"])
