from __future__ import annotations

import re
from typing import TYPE_CHECKING

from flogin import Query, RegexCondition, Result, SearchHandler

from .results import ChangeQueryResult

if TYPE_CHECKING:
    from .plugin import WordnikDictionaryPlugin

parts_of_speech = [
    "noun",
    "adjective",
    "verb",
    "adverb",
    "interjection",
    "pronoun",
    "preposition",
    "abbreviation",
    "affix",
    "article",
    "auxiliary-verb",
    "conjunction",
    "definite-article",
    "family-name",
    "given-name",
    "idiom",
    "imperative",
    "noun-plural",
    "noun-posessive",
    "past-participle",
    "phrasal-prefix",
    "proper-noun",
    "proper-noun-plural",
    "proper-noun-posessive",
    "suffix",
    "intransitive-verb",
    "transitive-verb",
]


class BaseHandler(SearchHandler):
    plugin: WordnikDictionaryPlugin | None  # type: ignore


class SelectModiferHandler(BaseHandler):
    async def callback(self, query: Query[re.Match]):
        match_data = query.condition_data
        assert match_data
        word = match_data["word"]

        return [
            Result(title="Modifier Selection Menu", score=100, icon="Images/app.png"),
            ChangeQueryResult(
                (f"{query.keyword} {word}!syllables"),
                title="Syllables",
                sub="Get the syllables of a word",
                icon="Images/app.png",
            ),
            ChangeQueryResult(
                (f"{query.keyword} {word}!similiar"),
                title="Similiar",
                sub="Get categories of similiar words",
                icon="Images/app.png",
            ),
            ChangeQueryResult(
                (f"{query.keyword} {word}!scrabble"),
                title="Scrabble",
                sub="Get the scrabble score of a word.",
                icon="Images/app.png",
            ),
            ChangeQueryResult(
                (f"{query.keyword} {word}!select-pos"),
                title="Filter by Part of Speech",
                sub="Filter results by the part of speech",
                icon="Images/app.png",
            ),
        ]


class SelectPosHandler(BaseHandler):
    async def callback(self, query: Query[re.Match]):
        match_data = query.condition_data
        assert match_data
        word = match_data["word"]

        yield Result(title="Part of Speech Selector", score=100, icon="Images/app.png")

        for pos in parts_of_speech:
            yield ChangeQueryResult(
                (f"{query.keyword} {word}!{pos}"), title=pos, icon="Images/app.png"
            )


class SyllablesHandler(BaseHandler):
    async def callback(self, query: Query[re.Match]):
        assert self.plugin

        match_data = query.condition_data
        assert match_data
        word = match_data["word"]

        return Result(await self.plugin.fetch_syllables(word), icon="Images/app.png")


class SimiliarHandler(BaseHandler):
    async def callback(self, query: Query[re.Match]):
        assert self.plugin

        match_data = query.condition_data
        assert match_data
        word = match_data["word"]

        self.plugin.preferred_keyword = query.keyword

        async for rel in self.plugin.fetch_word_relationships(word):
            yield rel


class ScrabbleHandler(BaseHandler):
    async def callback(self, query: Query[re.Match]):
        assert self.plugin

        match_data = query.condition_data
        assert match_data
        word = match_data["word"]

        value = await self.plugin.fetch_scrabble_score(word)
        return Result(
            f"Scrabble Score: {value}",
            icon="Images/app.png",
        )


class WordRelationshipHandler(BaseHandler):
    async def callback(self, query: Query[re.Match]):
        assert self.plugin

        match_data = query.condition_data
        assert match_data
        word = match_data["word"]
        relationship_name = match_data["relationship"]

        self.plugin.preferred_keyword = query.keyword

        rel_type = relationship_name.removeprefix("rel-")
        async for relationship in self.plugin.fetch_word_relationships(word):
            if relationship.type == rel_type:
                return relationship.get_word_options()


class FilterByPosHandler(BaseHandler):
    async def callback(self, query: Query[re.Match]):
        assert self.plugin

        match_data = query.condition_data
        assert match_data
        word = match_data["word"]
        pos = match_data["pos"].replace("-", " ")

        return [
            d
            async for d in self.plugin.fetch_definitions(word)
            if d.part_of_speech == pos
        ]


class InvalidModifierHandler(BaseHandler):
    async def callback(self, query: Query[re.Match]):
        assert self.plugin

        match_data = query.condition_data
        assert match_data
        word = match_data["word"]

        return ChangeQueryResult(
            (f"{query.keyword} {word}!select-modifier"),
            title="Unknown Search Modifier Given",
            sub="Press ENTER to open a select modifier menu.",
            icon="Images/error.png",
        )


def _c(raw_pattern: str) -> RegexCondition:
    return RegexCondition(re.compile(rf"^(?P<word>[a-zA-Z]+)!{raw_pattern}$"))


_pos_re = "|".join([f"({pos.replace('-', ' ')})" for pos in parts_of_speech])
handlers: list[SearchHandler] = [
    SelectModiferHandler(_c("select-modifier")),
    SelectPosHandler(_c("select-pos")),
    SyllablesHandler(_c("syllables")),
    SimiliarHandler(_c("similiar")),
    ScrabbleHandler(_c("scrabble")),
    WordRelationshipHandler(_c(r"rel-(?P<relationship>[a-zA-Z-_]*)")),
    FilterByPosHandler(_c(f"(?P<pos>{_pos_re})")),
    InvalidModifierHandler(_c(r".*")),
]
