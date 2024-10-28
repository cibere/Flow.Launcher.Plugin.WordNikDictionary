from __future__ import annotations

from .attributions import Attribution
from .dataclass import Dataclass
from .html_stripper import strip_tags
from .options import Option

__all__ = ("Definition",)


class Definition(Dataclass):
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

    def _generate_base_option(self) -> Option:
        return Option(
            title=self.text,
            sub=(
                f"{self.part_of_speech}; {self.attribution.text}"
                if self.part_of_speech
                else self.attribution.text
            ),
            callback="open_url",
            params=[self.wordnik_url],
        )

    def _generate_context_menu_options(self) -> list[Option]:
        temp = [Option(title=self.word, sub=self.text)]
        if self.part_of_speech:
            temp.append(
                Option(title=f"Part of Speech: {self.part_of_speech}"),
            )
        if self.wordnik_url:
            temp.append(Option.url("in Wordnik", self.wordnik_url))
        if self.attribution.url:
            temp.append(Option.url("Attribution", self.attribution.url))
        return temp
