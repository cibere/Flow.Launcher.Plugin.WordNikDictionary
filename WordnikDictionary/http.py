from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import quote_plus

import requests

from .errors import PluginException
from .options import Option
from .utils import dump_debug

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
        **kwargs,
    ) -> Any:
        if params is None:
            params = {}
        if headers is None:
            headers = {}

        headers["Accept"] = "application/json"
        params["api_key"] = self.settings["api_key"]
        url = f"https://api.wordnik.com/v4{endpoint}"
        res = requests.request(method, url, params=params, headers=headers, **kwargs)
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
            raise PluginException.wnf()

        res.raise_for_status()
        data = res.json()

        if self.debug:
            dump_debug("web_request_response", data)
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
            "useCanonical": self.settings["use_canonical"],
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
            "useCanonical": self.settings["use_canonical"],
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
            "useCanonical": self.settings["use_canonical"],
        }
        endpoint = f"/word.json/{quote_plus(word)}/relatedWords"

        return self.request("GET", endpoint, params=params)

    def fetch_urban_definition(self, word: str) -> list[dict]:
        url = "http://api.urbandictionary.com/v0/define"
        res = requests.get(url, params={"term": word})
        data = res.json()
        return data["list"]
