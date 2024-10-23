# -*- coding: utf-8 -*-

import sys, os

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, "lib"))
sys.path.append(os.path.join(parent_folder_path, "plugin"))

from flowlauncher import FlowLauncher
import requests, webbrowser
from urllib.parse import quote_plus


class HelloWorld(FlowLauncher):
    def query(self, query: str):
        """
        Docs on the endpoint
        https://developer.wordnik.com/docs#!/word/getDefinitions
        """
        
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
                {
                    "Title": definition["text"],
                    "SubTitle": definition['attributionText'],
                    "IcoPath": "Images/app.png",
                    "JsonRPCAction": {
                        "method": "open_url",
                        "parameters": [definition['wordnikUrl']]
                    }
                }
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
