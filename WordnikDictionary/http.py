from __future__ import annotations
from typing import TYPE_CHECKING
import requests
from urllib.parse import quote_plus
from typing import Any
import json
from WordnikDictionary.definition import Definition
from .errors import PluginException
from .options import Option

if TYPE_CHECKING:
    from .core import WordnikDictionaryPlugin

ICO_PATH = "Images/app.png"

bad_response = [
    {
        "citations": [],
        "exampleUses": [],
        "labels": [],
        "notes": [],
        "relatedWords": [],
        "textProns": [],
    },
    {
        "citations": [],
        "exampleUses": [],
        "labels": [],
        "notes": [],
        "relatedWords": [],
        "textProns": [],
    },
    {
        "citations": [],
        "exampleUses": [],
        "labels": [],
        "notes": [],
        "relatedWords": [],
        "textProns": [],
    },
    {
        "citations": [],
        "exampleUses": [],
        "labels": [],
        "notes": [],
        "relatedWords": [],
        "textProns": [],
    },
]


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

        res.raise_for_status()
        data = res.json()

        if data == bad_response:
            raise PluginException.create("No definition was found")

        if self.debug:
            with open("web_request_response.debug.json", "w") as f:
                json.dump(data, f, indent=4)
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
