from __future__ import annotations
from .options import Option
from .html_stripper import strip_tags
from .attributions import Attribution
from .dataclass import Dataclass

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
        return Option(title=self.type, sub=", ".join(self.words[:5]), callback="change_query", params=[f'def {self.word}!rel-{self.type}'])

    def get_word_options(self) -> list[Option]:
        return [
            Option(title=word, callback="change_query", params=[f'def {word}']) for word in self.words
        ]