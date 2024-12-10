from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from flogin import ExecuteResponse, Result

from .attributions import Attribution
from .html_stripper import strip_tags

if TYPE_CHECKING:
    from .plugin import WordnikDictionaryPlugin

__all__ = ("Definition",)


class Definition(Result):
    plugin: WordnikDictionaryPlugin | None  # type: ignore

    def __init__(
        self,
        part_of_speech: str | None,
        attribution: Attribution,
        text: str,
        wordnik_url: str,
        word: str,
    ) -> None:
        self.word: str = word
        self.attribution: Attribution = attribution
        self.text: str = strip_tags(text)
        self.wordnik_url: str = wordnik_url

        self.part_of_speech = part_of_speech
        if part_of_speech:
            self.part_of_speech = part_of_speech.strip(
                r"!@#$%^&*()-=_+[]{}\|';:\"/.,?><`~    "
            )

        super().__init__(
            title=self.text,
            sub=(
                f"{self.part_of_speech}; {self.attribution.text}"
                if self.part_of_speech
                else self.attribution.text
            ),
            icon="Images/app.png",
        )

    @classmethod
    def from_json(cls: type[Definition], word: str, data: dict) -> Definition | None:
        if data.get("text") is None:
            return None
        if isinstance(data["text"], list):
            text = ", ".join(data["text"])
        else:
            text = data["text"]
        return cls(
            data.get("partOfSpeech"),
            Attribution.from_json(data),
            text,
            data["wordnikUrl"],
            data["word"],
        )

    async def callback(self):
        assert self.plugin

        await self.plugin.api.open_url(self.wordnik_url)
        return ExecuteResponse()

    async def context_menu(self):
        assert self.plugin

        yield Result(
            f"Word: {self.word}",
            sub="Press CTRL + C to copy",
            copy_text=self.word,
            icon="Images/app.png",
        )
        yield Result(
            f"Definition: {self.text}",
            sub="Press CTRL + C to copy",
            copy_text=self.text,
            icon="Images/app.png",
        )
        if self.part_of_speech is not None:
            yield Result(
                f"Part of Speech: {self.part_of_speech}",
                sub="Press CTRL + C to copy",
                copy_text=self.part_of_speech,
                icon="Images/app.png",
            )

        yield Result.create_with_partial(
            partial(self.plugin.api.open_url, self.wordnik_url),
            title=f"Wordnik URL: {self.wordnik_url}",
            sub="Press CTRL + C to copy, cick to open",
            copy_text=self.wordnik_url,
            icon="Images/app.png",
        )

        if self.attribution.text:
            yield Result(
                f"Attribution: {self.attribution.text}",
                sub="Press CTRL+C to copy",
                copy_text=self.attribution.text,
                icon="Images/app.png",
            )
        if self.attribution.url:
            yield Result.create_with_partial(
                partial(self.plugin.api.open_url, self.attribution.url),
                title=f"Attribution URL: {self.attribution.url}",
                sub="Press CTRL+C to copy, click to open",
                copy_text=self.attribution.url,
                icon="Images/app.png",
            )
