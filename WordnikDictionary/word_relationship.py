from __future__ import annotations

from typing import TYPE_CHECKING

from flogin import ExecuteResponse, Result

if TYPE_CHECKING:
    from .plugin import WordnikDictionaryPlugin

__all__ = ("WordRelationship", "WordResult")


class WordResult(Result):
    plugin: WordnikDictionaryPlugin | None  # type: ignore

    def __init__(self, word: str):
        super().__init__(title=word, icon="Images/app.png")

    async def callback(self):
        assert self.plugin

        await self.plugin.api.change_query(
            f"{self.plugin.preferred_keyword} {self.title}"
        )
        return ExecuteResponse(hide=False)


class WordRelationship(Result):
    plugin: WordnikDictionaryPlugin | None  # type: ignore

    def __init__(self, word: str, type: str, words: list[str]) -> None:
        self.word: str = word
        self.type: str = type
        self.words: list[str] = words

        super().__init__(
            title=self.type, sub=", ".join(self.words[:5]), icon="Images/app.png"
        )

    async def callback(self):
        assert self.plugin

        await self.plugin.api.change_query(
            f"{self.plugin.preferred_keyword} {self.word}!rel-{self.type}"
        )
        return ExecuteResponse(hide=False)

    @classmethod
    def from_json(
        cls: type[WordRelationship], word: str, data: dict
    ) -> WordRelationship | None:
        return cls(word, data["relationshipType"], data["words"])

    async def context_menu(self):
        return [
            Result(icon="Images/app.png", title=f"Original Word: {self.word}"),
            Result(icon="Images/app.png", title=f"Chosen Category: {self.type}"),
            Result(
                icon="Images/app.png",
                title="Go back and click on the category to see a full list of the words.",
            ),
        ]

    def get_word_options(self) -> list[Result]:
        return [WordResult(word.lower()) for word in self.words]
