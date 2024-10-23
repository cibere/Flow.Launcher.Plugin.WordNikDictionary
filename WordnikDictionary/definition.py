from __future__ import annotations
from .options import Option
from .html_stripper import strip_tags

__all__ = "Definition", "Attribution"


class Attribution:
    def __init__(self, text: str, url: str) -> None:
        self.text = text
        self.url = url


class Definition:
    """
    This dataclass represents the definition object returned by wordnik's api
    """

    def __init__(
        self,
        id: str,
        part_of_speech: str,
        attribution: Attribution,
        text: str,
        wordnik_url: str,
        word: str,
    ) -> None:
        self.word = word
        self.id = id
        self.part_of_speech = part_of_speech
        self.attribution = attribution
        self.text = strip_tags(text)
        self.wordnik_url = wordnik_url

    @classmethod
    def from_json(cls: type[Definition], data: dict) -> Definition:
        return cls(
            data["id"],
            data["partOfSpeech"],
            Attribution(data["attributionText"], data["attributionUrl"]),
            data["text"],
            data["wordnikUrl"],
            data["word"],
        )

    def _generate_base_option(self) -> Option:
        return Option(
            title=self.text,
            sub=self.attribution.text,
            callback="open_url",
            params=[self.wordnik_url],
        )

    def _generate_context_menu_options(self) -> list[Option]:
        return [
            Option(title=self.word, sub=self.text),
            Option(title=f"Part of Speech: {self.part_of_speech}"),
            Option.url("in Wordnik", self.wordnik_url),
            Option.url("Attribution", self.attribution.url),
        ]

    def to_option(self) -> Option:
        opt = self._generate_base_option()
        opt.context_data = self._generate_context_menu_options()
        return opt
