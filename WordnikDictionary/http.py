from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any
from urllib.parse import quote_plus

import requests

from .errors import PluginException
from .options import Option

LOG = getLogger(__name__)
if TYPE_CHECKING:
    from .core import WordnikDictionaryPlugin

ICO_PATH = "Images/app.png"


class HTTPClient:

    def __init__(self, flow: WordnikDictionaryPlugin):
        self.flow = flow

    @property
    def settings(self) -> dict:
        return self.flow.rpc_request["settings"]

    @property
    def debug(self) -> bool:
        try:
            return self.settings["debug_mode"]
        except TypeError:
            return True

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        raise_wnf_on_404: bool = True,
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
        res = requests.request(method, url, params=params, headers=headers, **kwargs)
        data = res.json()
        LOG.debug(
            f"Received HTTP response. {res.status_code=}, {res.headers=}, {data=}"
        )
        if res.status_code == 401:
            opt = Option(
                title="Invalid API Key",
                sub="Click ENTER for instructions on how to get a valid API key",
                callback="open_url",
                params=[
                    "https://github.com/cibere/Flow.Launcher.Plugin.WordNikDictionary?tab=readme-ov-file#get-an-api-key"
                ],
            )
            raise PluginException(opt.title, [opt])
        elif res.status_code == 404:
            if raise_wnf_on_404:
                raise PluginException.wnf()
            else:
                return data

        res.raise_for_status()

        return data

    def fetch_definitions(self, word: str) -> list[dict[str, Any]]:
        """
        Docs on the endpoint
        https://developer.wordnik.com/docs#!/word/getDefinitions
        """

        try:
            limit = int(self.settings["results"])
        except ValueError:
            opt = Option(
                title="Error: Invalid Results Value Given.",
                sub="The Results settings item must be a valid number.",
                callback="open_settings_menu",
            )
            raise PluginException(opt.title, [opt])

        params = {
            "limit": limit,
            "includeRelated": False,
            "includeTags": False,
        }
        endpoint = f"/word.json/{quote_plus(word)}/definitions"

        return self.request("GET", endpoint, params=params)

    def fetch_syllables(self, word: str) -> list[dict[str, Any]]:
        """
        Docs on the endpoint
        https://developer.wordnik.com/docs#!/word/getHyphenation
        """

        params = {
            "limit": 50,
        }
        endpoint = f"/word.json/{quote_plus(word)}/hyphenation"

        return self.request("GET", endpoint, params=params)

    def fetch_similiar_words(self, word: str) -> list[dict[str, Any]]:
        """
        Docs on the endpoint
        https://developer.wordnik.com/docs#!/word/getRelatedWords
        """

        try:
            limit = int(self.settings["results"])
        except ValueError:
            opt = Option(
                title="Error: Invalid Results Value Given.",
                sub="The Results settings item must be a valid number.",
                callback="open_settings_menu",
            )
            raise PluginException(opt.title, [opt])

        params = {
            "limit": limit,
        }
        endpoint = f"/word.json/{quote_plus(word)}/relatedWords"

        return self.request("GET", endpoint, params=params)

    def fetch_word_list_file(self) -> Any:
        """
        Source: https://github.com/dwyl/english-words
        """
        url = "https://raw.githubusercontent.com/dwyl/english-words/refs/heads/master/words_alpha.txt"
        res = requests.get(url)
        res.raise_for_status()
        return res.content

    def fetch_scrabble_score(self, word: str) -> dict[str, int]:
        """
        Docs on the endpoint
        https://developer.wordnik.com/docs#!/word/getScrabbleScore
        """

        endpoint = f"/word.json/{quote_plus(word)}/scrabbleScore"

        return self.request("GET", endpoint, raise_wnf_on_404=False)