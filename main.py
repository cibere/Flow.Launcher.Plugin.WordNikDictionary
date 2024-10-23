import sys, os

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, "lib"))
sys.path.append(os.path.join(parent_folder_path, "plugin"))

from flowlauncher import FlowLauncher, FlowLauncherAPI
import requests, webbrowser
from urllib.parse import quote_plus
from typing import Any
import json
from html_stripper import strip_tags


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


class WordnikDictionaryPlugin(FlowLauncher):
    @property
    def settings(self) -> dict:
        return self.rpc_request["settings"]

    @property
    def debug(self) -> bool:
        try:
            return self.settings["debug_mode"]
        except TypeError:
            return True

    def generate_json(
        self,
        *,
        title: str,
        sub: str = "",
        callback: str = "",
        params: list[str] = [],
        context_data: list[Any] = [],
    ) -> dict:
        data: dict[str, Any] = {
            "Title": title,
            "SubTitle": sub,
            "IcoPath": "Images/app.png",
            "ContextData": context_data,
        }
        if callback:
            data["JsonRPCAction"] = {"method": callback, "parameters": params}
        return data

    def query(self, query: str):
        """
        Docs on the endpoint
        https://developer.wordnik.com/docs#!/word/getDefinitions
        """

        if self.debug:
            with open("rpc_data.debug.json", "w") as f:
                json.dump(self.rpc_request, f, indent=4)

        if not query:
            return [self.generate_json(title="Invalid Word Given")]

        url = f"https://api.wordnik.com/v4/word.json/{quote_plus(query)}/definitions"

        try:
            limit = int(self.settings["results"])
        except ValueError:
            return [
                self.generate_json(
                    title="Error: Invalid Results Value Given.",
                    sub="The Results settings item must be a valid number.",
                    callback="open_settings_menu",
                )
            ]

        params = {
            "limit": limit,
            "includeRelated": False,
            "useCanonical": self.settings["use_canonical"],
            "includeTags": False,
            "api_key": self.settings["api_key"],
        }
        headers = {"Accept": "application/json"}
        res = requests.get(url, params=params, headers=headers)
        res.raise_for_status()
        data = res.json()

        if data == bad_response:
            return [self.generate_json(title="No Definition was found")]

        if self.debug:
            with open("web_request_response.debug.json", "w") as f:
                json.dump(data, f, indent=4)

        final = []

        for definition in data:
            final.append(
                self.generate_json(
                    title=strip_tags(definition["text"]),
                    sub=definition["attributionText"],
                    callback="open_url",
                    params=[definition["wordnikUrl"]],
                    context_data=[
                        self.generate_json(
                            title="Open Wordnik URL",
                            sub=definition["wordnikUrl"],
                            callback="open_url",
                            params=[definition["wordnikUrl"]],
                        ),
                        self.generate_json(
                            title="Open Attribution Website",
                            sub=definition["attributionUrl"],
                            callback="open_url",
                            params=[definition["attributionUrl"]],
                        ),
                    ],
                )
            )

        return final

    def context_menu(self, data: list[Any]):
        if self.debug:
            with open("rpc_data.debug.json", "w") as f:
                json.dump(self.rpc_request, f, indent=4)
            with open("context_menu_data.debug.json", "w") as f:
                json.dump(data, f, indent=4)
        return data

    def open_url(self, url):
        webbrowser.open(url)

    def open_settings_menu(self):
        FlowLauncherAPI.open_setting_dialog()


if __name__ == "__main__":
    WordnikDictionaryPlugin()
