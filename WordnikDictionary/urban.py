from __future__ import annotations

from .dataclass import Dataclass
from .options import Option

__all__ = ("UrbanDefinition",)


class UrbanDefinition(Dataclass):
    def __init__(
        self,
        word: str,
        text: str,
        permalink: str,
        upvotes: int,
        downvotes: int,
        author: str,
        example: str,
        created: str,
    ) -> None:
        self.word: str = word
        self.text = text
        self.permalink = permalink
        self.upvotes = upvotes
        self.downvotes = downvotes
        self.author = author
        self.example = example
        self.created = created

    @classmethod
    def from_json(
        cls: type[UrbanDefinition], _: str, data: dict
    ) -> UrbanDefinition | None:
        return cls(
            data["word"],
            data["definition"].replace("\n", " "),
            data["permalink"],
            data["thumbs_up"],
            data["thumbs_down"],
            data["author"],
            data["example"],
            data["written_on"],
        )

    def _generate_base_option(self) -> Option:
        return Option(
            title=self.text,
            sub=f"{self.upvotes}:{self.downvotes} - by {self.author}",
            callback="open_url",
            params=[self.permalink],
        )

    def _generate_context_menu_options(self) -> list[Option]:
        return [
            Option(title=self.text),
            Option(title=f"Author: {self.author}"),
            Option(title=f"Upvotes: {self.upvotes}"),
            Option(title=f"Downvotes: {self.downvotes}"),
            Option(title=f"Example: {self.example}"),
            Option.url("Urban Permalink", self.permalink),
        ]
