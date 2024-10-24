import re
import webbrowser
from typing import Any

from flowlauncher import FlowLauncher, FlowLauncherAPI

from .definition import Definition
from .http import HTTPClient
from .options import Option
from .utils import convert_options, dump_debug, handle_plugin_exception
from .word_relationship import WordRelationship

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
    "verb-intransitive",
    "verb-transitive",
]


class WordnikDictionaryPlugin(FlowLauncher):
    def __init__(self, *args, **kwargs) -> None:
        self.http = HTTPClient(self)
        super().__init__(*args, **kwargs)

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
        if self.debug:
            dump_debug("rpc_data", self.rpc_request)

        if not query.strip():
            return [Option.wnf()]

        word = query
        filter_query = None
        matches = QUERY_REGEX.match(query)
        if matches:
            word = matches["word"]
            filter_query = matches.group("filter")

        if filter_query:
            if filter_query == "syllables":
                syllables = self.get_syllables(word)
                return [Option(title="-".join(syllables))] or [Option.wnf()]
            if filter_query == "similiar":
                return self.get_word_relationships(word) or [Option.wnf()]
            if filter_query.startswith("rel-"):
                rel_type = filter_query.removeprefix("rel-")
                relationships = self.get_word_relationships(word)
                for relationship in relationships:
                    if relationship.type == rel_type:
                        return relationship.get_word_options() or [Option.wnf()]

        definitions = self.get_definitions(word)

        if filter_query in parts_of_speech:
            temp = filter_query.replace("-", " ")
            definitions = filter(lambda d: d.part_of_speech == temp, definitions)

        return definitions or [Option.wnf()]

    @handle_plugin_exception
    def context_menu(self, data: list[Any]):
        if self.debug:
            dump_debug("rpc_data", self.rpc_request)
            dump_debug("context_menu_data", data)
        return data

    def open_url(self, url):
        webbrowser.open(url)

    def open_settings_menu(self):
        FlowLauncherAPI.open_setting_dialog()

    def change_query(self, query: str):
        FlowLauncherAPI.change_query(query)
