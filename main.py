# -*- coding: utf-8 -*-

import sys, os

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, "lib"))
sys.path.append(os.path.join(parent_folder_path, "plugin"))

from flowlauncher import FlowLauncher
import requests, webbrowser
from urllib.parse import quote_plus
from typing import Any

ICO_PATH = "Images/app.png"


class HelloWorld(FlowLauncher):
    def generate_json(
        self, *, title: str, sub: str = "", callback: str = "", params: list[str] = []
    ) -> dict:
        data: dict[str, Any] = {
            "Title": title,
            "SubTitle": sub,
            "IcoPath": "Images/app.png",
        }
        if callback:
            data["JsonRPCAction"] = {"method": callback, "parameters": params}
        return data

    def query(self, query: str):
        """
        Docs on the endpoint
        https://developer.wordnik.com/docs#!/word/getDefinitions
        """

        if not query:
            return [self.generate_json(title="Invalid Word Given")]

        url = f"https://api.wordnik.com/v4/word.json/{quote_plus(query)}/definitions"
        params = {
            "limit": 20,
            "includeRelated": False,
            "useCanonical": False,
            "includeTags": False,
            "api_key": "c23b746d074135dc9500c0a61300a3cb7647e53ec2b9b658e",
        }
        headers = {"Accept": "application/json"}
        res = requests.get(url, params=params, headers=headers)
        res.raise_for_status()  # ! get rid of this after testing
        data = res.json()
        final = []

        for definition in data:
            final.append(
                self.generate_json(
                    title=definition["text"],
                    sub=definition["attributionText"],
                    callback="open_url",
                    params=[definition["wordnikUrl"]],
                )
            )

        return final

    def context_menu(self, data):
        return [
            {
                "Title": "Hello World Python's Context menu",
                "SubTitle": "Press enter to open Flow the plugin's repo in GitHub",
                "IcoPath": "Images/app.png",
                "JsonRPCAction": {
                    "method": "open_url",
                    "parameters": [
                        "https://github.com/Flow-Launcher/Flow.Launcher.Plugin.WordNikDictionary"
                    ],
                },
            }
        ]

    def open_url(self, url):
        webbrowser.open(url)


if __name__ == "__main__":
    HelloWorld()
