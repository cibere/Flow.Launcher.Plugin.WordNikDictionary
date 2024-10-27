from __future__ import annotations

from .dataclass import Dataclass
from .options import Option

__all__ = ("WordRelationship",)


class WordRelationship(Dataclass):
    def __init__(self, word: str, type: str, words: list[str]) -> None:
        self.word: str = word
        self.type: str = type
        self.words: list[str] = words

    @classmethod
    def from_json(
        cls: type[WordRelationship], word: str, data: dict
    ) -> WordRelationship | None:
        return cls(word, data["relationshipType"], data["words"])

    def _generate_base_option(self) -> Option:
        return Option(
            title=self.type,
            sub=", ".join(self.words[:5]),
            callback="change_query",
            params=[f"{self.word}!rel-{self.type}"],
            hide_after_callback=False,
        )

    def _generate_context_menu_options(self) -> list[Option]:
        return [
            Option(title=f"Original Word: {self.word}"),
            Option(title=f"Chosen Category: {self.type}"),
            Option(
                title="Go back and click on the category to see a full list of the words."
            ),
        ]

    def get_word_options(self) -> list[Option]:
        return [
            Option(
                title=word,
                callback="change_query",
                params=[word],
                hide_after_callback=False,
                context_data=[
                    Option(title=f"Chosen Word: {word}"),
                    Option(title=f"Go back and click on the word to see definitions."),
                ],
            )
            for word in self.words
        ]
