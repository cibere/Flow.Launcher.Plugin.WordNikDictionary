from __future__ import annotations

from typing import Self

from .options import Option

__all__ = ("Dataclass",)


class Dataclass:
    @classmethod
    def from_json(cls: type[Self], word: str, data: dict) -> Self | None:
        raise RuntimeError("This must be overriden")

    def _generate_base_option(self) -> Option:
        raise RuntimeError("This must be overriden")

    def _generate_context_menu_options(self) -> list[Option]:
        return []

    def to_option(self) -> Option:
        opt = self._generate_base_option()
        opt.context_data = self._generate_context_menu_options()
        return opt
