from __future__ import annotations

from typing import AsyncIterator

import aiohttp, asyncio, logging
from flogin import Plugin

from .definition import Definition
from .http import HTTPClient
from .search_modifiers import handlers as search_modifier_handlers
from .word_relationship import WordRelationship


class WordnikDictionaryPlugin(Plugin):
    http: HTTPClient
    preferred_keyword: str

    def __init__(self):
        super().__init__()

        self.register_search_handlers(*search_modifier_handlers)

    async def fetch_definitions(self, word: str) -> AsyncIterator[Definition]:
        raw = await self.http.fetch_definitions(word)

        for data in raw:
            definition = Definition.from_json(word, data)
            if definition:
                yield definition

    async def fetch_syllables(self, word: str) -> str:
        raw = await self.http.fetch_syllables(word)

        syllables = []
        for data in sorted(raw, key=lambda d: d["seq"]):
            syllables.append(data["text"])

        syll = "-".join(syllables)
        return syll

    async def fetch_word_relationships(
        self, word: str
    ) -> AsyncIterator[WordRelationship]:
        raw = await self.http.fetch_similiar_words(word)

        for data in raw:
            item = WordRelationship.from_json(word, data)
            if item:
                yield item

    async def fetch_scrabble_score(self, word: str) -> int:
        data = await self.http.fetch_scrabble_score(word)
        val = data.get("value") or 0
        return val
    
    async def start(self):
        loop = asyncio.get_event_loop()
        logging.getLogger("asyncio").handlers.clear()
        logging.getLogger("asyncio").setLevel(logging.NOTSET)
        loop.set_debug(True)
        logging.getLogger("asyncio").handlers.clear()
        logging.getLogger("asyncio").setLevel(logging.NOTSET)

        async with aiohttp.ClientSession() as cs:
            self.http = HTTPClient(self, cs)
            await super().start()