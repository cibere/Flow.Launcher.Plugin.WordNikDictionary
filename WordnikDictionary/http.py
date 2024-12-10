from __future__ import annotations

from functools import partial
from logging import getLogger
from typing import TYPE_CHECKING, Any, Coroutine, TypeVar
from urllib.parse import quote_plus

import aiohttp
from flogin import Result, Settings
from flogin.utils import cached_coro

from .errors import PluginException, WordNotFound

if TYPE_CHECKING:
    from .plugin import WordnikDictionaryPlugin

    T = TypeVar("T")
    Awaitable = Coroutine[Any, Any, T]
else:
    Awaitable = Any
    
LOG = getLogger(__name__)

ICO_PATH = "Images/app.png"


class HTTPClient:
    def __init__(self, flow: WordnikDictionaryPlugin, session: aiohttp.ClientSession):
        self.flow = flow
        self.session: aiohttp.ClientSession = session

    @property
    def settings(self) -> Settings:
        return self.flow.settings

    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs,
    ) -> Any:
        if params is None:
            params = {}
        if headers is None:
            headers = {}

        headers["Accept"] = "application/json"
        params["api_key"] = self.settings["api_key"]
        url = f"https://api.wordnik.com/v4{endpoint}"
        LOG.debug(f"Sending HTTP request. {url=}, {params=}, {headers=}, {kwargs=}")
        res = await self.session.request(
            method, url, params=params, headers=headers, **kwargs
        )
        data = await res.json()
        LOG.debug(f"Received HTTP response. {res.status=}, {res.headers=}, {data=}")
        if res.status == 401:
            raise PluginException(
                "Invalid API Key",
                Result.create_with_partial(
                    partial(
                        self.flow.api.open_url,
                        "https://github.com/cibere/Flow.Launcher.Plugin.WordNikDictionary?tab=readme-ov-file#get-an-api-key",
                    ),
                    title="Invalid API Key",
                    sub="Click ENTER for instructions on how to get a valid API key",
                ),
            )

        res.raise_for_status()

        return data

    @cached_coro
    def fetch_definitions(self, word: str) -> Awaitable[list[dict[str, Any]]]:
        """
        Docs on the endpoint
        https://developer.wordnik.com/docs#!/word/getDefinitions
        """

        try:
            limit = int(self.settings["results"])
        except ValueError:
            raise PluginException(
                "Invalid Results Value Given",
                Result.create_with_partial(
                    self.flow.api.open_settings_menu,
                    title="Error: Invalid Results Value Given.",
                    sub="The Results settings item must be a valid number.",
                ),
            )
        
        ew = quote_plus(word)

        LOG.debug(f"Getting definition for {ew!r}")

        params = {
            "limit": limit,
            # "includeRelated": False,
            # "includeTags": False,
        }
        endpoint = f"/word.json/{ew}/definitions"

        try:
            return self.request("GET", endpoint, params=params)
        except aiohttp.ClientResponseError as e:
            if e.code == 404:
                raise WordNotFound(word)
            raise

    @cached_coro
    def fetch_syllables(self, word: str) -> Awaitable[list[dict[str, Any]]]:
        """
        Docs on the endpoint
        https://developer.wordnik.com/docs#!/word/getHyphenation
        """

        params = {
            "limit": 50,
        }
        endpoint = f"/word.json/{quote_plus(word)}/hyphenation"

        return self.request("GET", endpoint, params=params)

    @cached_coro
    def fetch_similiar_words(self, word: str) -> Awaitable[list[dict[str, Any]]]:
        """
        Docs on the endpoint
        https://developer.wordnik.com/docs#!/word/getRelatedWords
        """

        try:
            limit = int(self.settings["results"])
        except ValueError:
            raise PluginException(
                "Invalid Results Value Given",
                Result.create_with_partial(
                    self.flow.api.open_settings_menu,
                    title="Error: Invalid Results Value Given.",
                    sub="The Results settings item must be a valid number.",
                ),
            )

        params = {
            "limit": limit,
        }
        endpoint = f"/word.json/{quote_plus(word)}/relatedWords"

        return self.request("GET", endpoint, params=params)

    @cached_coro
    async def fetch_word_list_file(self) -> Any:
        """
        Source: https://github.com/dwyl/english-words
        """
        url = "https://raw.githubusercontent.com/dwyl/english-words/refs/heads/master/words_alpha.txt"
        res = await self.session.get(url)
        res.raise_for_status()
        return res.content

    @cached_coro
    def fetch_scrabble_score(self, word: str) -> Awaitable[dict[str, int]]:
        """
        Docs on the endpoint
        https://developer.wordnik.com/docs#!/word/getScrabbleScore
        """

        endpoint = f"/word.json/{quote_plus(word)}/scrabbleScore"

        return self.request("GET", endpoint)
