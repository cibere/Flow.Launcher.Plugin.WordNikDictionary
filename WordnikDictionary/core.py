import inspect
import json
import os
import re
import sys
import webbrowser
from logging import getLogger
from typing import Any

from flowlauncher import FlowLauncher, FlowLauncherAPI

from .definition import Definition
from .errors import InternalException
from .http import HTTPClient
from .options import Option
from .utils import convert_options, handle_plugin_exception
from .word_relationship import WordRelationship

LOG = getLogger(__name__)
QUERY_REGEX = re.compile(r"^(?P<word>[a-zA-Z]+)(!(?P<filter>[a-zA-Z-]+))?$")

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


class WordnikDictionaryPlugin(FlowLauncher):
    def __init__(self, args: str | None = None):
        self.http = HTTPClient(self)

        # defalut jsonrpc
        self.rpc_request = {"method": "query", "parameters": [""]}
        self.debugMessage = ""

        if args is None and len(sys.argv) > 1:

            # Gets JSON-RPC from Flow Launcher process.
            self.rpc_request = json.loads(sys.argv[1])
        LOG.debug(f"Received RPC request: {json.dumps(self.rpc_request)}")

        # proxy is not working now
        # self.proxy = self.rpc_request.get("proxy", {})

        request_method_name = self.rpc_request.get("method", "query")
        request_parameters = self.rpc_request.get("parameters", [])

        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        request_method = dict(methods)[request_method_name]
        results = request_method(*request_parameters)

        if request_method_name in ("query", "context_menu"):
            data = {"result": results, "debugMessage": self.debugMessage}

            try:
                payload = json.dumps(data)
            except TypeError as e:
                LOG.error(
                    f"Error occured while trying to convert payload for flow through json.dumps. Data: {data!r}",
                    exc_info=e,
                )
                raise InternalException() from e
            else:
                LOG.debug(f"Sending data to flow: {payload}")
                print(payload)

    @property
    def settings(self) -> dict:
        return self.rpc_request["settings"]

    def get_definitions(self, word: str) -> list[Definition]:
        raw = self.http.fetch_definitions(word)
        final = []
        for data in raw:
            definition = Definition.from_json(word, data)
            if definition:
                final.append(definition)
        return final

    def get_syllables(self, word: str) -> list[str]:
        raw = self.http.fetch_syllables(word)
        final = []
        for data in sorted(raw, key=lambda d: d["seq"]):
            final.append(data["text"])
        return final

    def get_word_relationships(self, word: str) -> list[WordRelationship]:
        raw = self.http.fetch_similiar_words(word)
        final = []
        for data in raw:
            item = WordRelationship.from_json(word, data)
            if item:
                final.append(item)
        return final

    @handle_plugin_exception
    @convert_options
    def query(self, query: str):
        LOG.info(f"Received query: {query!r}")

        if not query.strip():
            return [Option.wnf()]

        word = query
        filter_query = None
        matches = QUERY_REGEX.match(query)
        if matches:
            word = matches["word"]
            filter_query = matches.group("filter")
            LOG.info(f"Match found. {word=}, {filter_query=}")

        if filter_query:
            if filter_query == "syllables":
                syllables = self.get_syllables(word)
                return [Option(title="-".join(syllables))] or [Option.wnf()]
            elif filter_query == "similiar":
                return self.get_word_relationships(word) or [Option.wnf()]
            elif filter_query.startswith("rel-"):
                rel_type = filter_query.removeprefix("rel-")
                relationships = self.get_word_relationships(word)
                for relationship in relationships:
                    if relationship.type == rel_type:
                        return relationship.get_word_options() or [Option.wnf()]

        definitions = self.get_definitions(word)

        if filter_query:
            if filter_query in parts_of_speech:
                temp = filter_query.replace("-", " ")
                definitions = filter(lambda d: d.part_of_speech == temp, definitions)
            else:
                return [
                    Option(
                        title="Unknown Search Modifier Given",
                        sub="Press ENTER to open search modifier index",
                        callback="open_url",
                        params=[
                            "https://github.com/cibere/Flow.Launcher.Plugin.WordNikDictionary/tree/v2?tab=readme-ov-file#search-modifiers"
                        ],
                    )
                ]

        return definitions or [Option.wnf()]

    @handle_plugin_exception
    def context_menu(self, data: list[Any]):
        LOG.debug(f"Context menu received: {data=}")
        return data

    def open_url(self, url):
        webbrowser.open(url)

    def open_settings_menu(self):
        FlowLauncherAPI.open_setting_dialog()

    def change_query(self, query: str):
        FlowLauncherAPI.change_query(query)

    def open_log_file_folder(self):
        os.system(f'explorer.exe /select, "wordnik.logs"')
