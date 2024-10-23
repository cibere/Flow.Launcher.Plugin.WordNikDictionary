from flowlauncher import FlowLauncher, FlowLauncherAPI
import webbrowser
from typing import Any
import json
from .definition import Definition
from .errors import PluginException
from .http import HTTPClient
from .utils import handle_plugin_exception


class WordnikDictionaryPlugin(FlowLauncher):
    cache: dict[str, list[Definition]]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.http = HTTPClient(self)
        self.cache = {}

    @property
    def settings(self) -> dict:
        return self.rpc_request["settings"]

    @property
    def debug(self) -> bool:
        try:
            return self.settings["debug_mode"]
        except TypeError:
            return True

    def get_definitions(self, word: str) -> list[Definition]:
        items = self.cache.get(word, None)
        if items is None:
            raw = self.http.fetch_definitions(word)
            self.cache[word] = items = [Definition.from_json(data) for data in raw]
        return items

    @handle_plugin_exception
    def query(self, query: str):
        if self.debug:
            with open("rpc_data.debug.json", "w") as f:
                json.dump(self.rpc_request, f, indent=4)

        if not query:
            raise PluginException.create("Invalid Word Given")

        definitions = self.get_definitions(query)
        return [d.to_option() for d in definitions]

    @handle_plugin_exception
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
