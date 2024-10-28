import inspect
import json
import os
import re
import sys
import webbrowser
from difflib import SequenceMatcher, get_close_matches
from logging import getLogger
from typing import Any

from flowlauncher import FlowLauncherAPI

from .dataclass import Dataclass
from .definition import Definition
from .errors import BasePluginException, InternalException
from .http import HTTPClient
from .options import Option
from .word_relationship import WordRelationship

LOG = getLogger(__name__)
QUERY_REGEX = re.compile(r"^(?P<word>[a-zA-Z]+)(!(?P<filter>[a-zA-Z-_]+))?$")
DEFAULT_WORD_LIST_LOC = "WordnikDictionary/word_list.txt"

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


class WordnikDictionaryPlugin:
    def __init__(self, args: str | None = None):
        self.http = HTTPClient(self)

        # defalut jsonrpc
        self.rpc_request = {"method": "query", "parameters": [""]}

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
        if request_method_name in ("query", "context_menu"):
            try:
                raw_results = request_method(*request_parameters)
            except BasePluginException as e:
                raw_results = e.options
            except Exception as e:
                LOG.error(
                    f"Error happened while running {request_method_name!r} method.",
                    exc_info=e,
                )
                raw_results = InternalException().options
            final_results = []

            for result in raw_results:
                if isinstance(result, Dataclass):
                    result = result.to_option()
                if isinstance(result, Option):
                    result = result.to_jsonrpc()
                if isinstance(result, dict):
                    final_results.append(result)
                else:
                    LOG.error(
                        f"Unknown result given: {result!r}",
                        exc_info=RuntimeError(f"Unknown result given: {result!r}"),
                    )
                    final_results = InternalException().final_options()
                    break

            data = {"result": final_results}

            payload = json.dumps(data)
            LOG.debug(f"Sending data to flow: {payload}")
            print(payload)
        else:
            request_method(*request_parameters)

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

    def handle_wnf(self, word: str) -> list[Option]:
        if self.settings["spellcheck_autocomplete"]:
            loc = self.settings.get("wordlist_loc", None) or DEFAULT_WORD_LIST_LOC
            custom = loc != DEFAULT_WORD_LIST_LOC
            exists = os.path.exists(loc)
            if not exists:
                if custom:
                    return [
                        Option(
                            title="Word List file not found.", score=100, icon="error"
                        ),
                        Option(
                            title="Are you sure you gave the right file location?",
                            sub="Make sure you gave an absolute path",
                            score=50,
                            icon="error",
                        ),
                        Option(
                            title="Open Flow Launcher Settings",
                            score=0,
                            callback="open_settings_menu",
                        ),
                    ]
                return [
                    Option(title="Word List file not found.", icon="error", score=100),
                    Option(
                        title="Download Latest File",
                        callback="download_word_list",
                        icon="error",
                    ),
                    Option(
                        title="Open Settings to choose custom file",
                        callback="open_settings_menu",
                        icon="error",
                    ),
                ]
            try:
                with open(loc, "r") as f:
                    word_list = f.read().split("\n")
            except PermissionError as e:
                if custom:
                    LOG.debug(f"Permission error encountered", exc_info=e)
                    return [
                        Option(
                            title="Permission Error encountered when trying to open wordlist.",
                            sub="Make sure the wordlist is in a directory that Flow Launcher has permissions to access.",
                            icon="error",
                        )
                    ]
                else:
                    raise InternalException() from e
            if word in word_list:
                return [Option(title="No Results Found")]
            matches = get_close_matches(word, word_list, n=10)
            final: list[Option] = []

            for found_word in matches:
                score = SequenceMatcher(None, word, found_word).ratio() * 100

                final.append(
                    Option(
                        title=found_word,
                        sub=score,
                        callback="change_query",
                        params=[f"{found_word}"],
                    )
                )
            final = sorted(final, key=lambda opt: opt.sub, reverse=True)
            for idx, res in enumerate(final):
                res.score = len(final) - idx
                res.sub = f"Certainty: {res.sub}%"

            if final:
                return [
                    Option(
                        title="Word Not Found, did you mean...", icon="error", score=110
                    )
                ] + final
            else:
                return [
                    Option(
                        title="Word Not Found, could not find any similiar words.",
                        icon="error",
                        score=110,
                    )
                ]
        else:
            return [Option.wnf()]

    def query(self, query: str):
        LOG.info(f"Received query: {query!r}")

        if not query.strip():
            return self.handle_wnf(query)

        word = query
        filter_query = None
        matches = QUERY_REGEX.match(query)
        if matches:
            word = matches["word"]
            filter_query = matches.group("filter")
            LOG.info(f"Match found. {word=}, {filter_query=}")

        if filter_query:
            if filter_query == "select-modifier":
                return [
                    Option(title="Modifier Selection Menu", score=100),
                    Option(
                        title="Syllables",
                        sub="Get the syllables of a word",
                        callback="change_query",
                        params=[f"{word}!syllables"],
                    ),
                    Option(
                        title="Similiar",
                        sub="Get categories of similiar words",
                        callback="change_query",
                        params=[f"{word}!similiar"],
                    ),
                    Option(
                        title="Filter by Part of Speech",
                        sub="Filter results by the part of speech",
                        callback="change_query",
                        params=[f"{word}!select-pos"],
                    ),
                ]
            if filter_query == "select-pos":
                return [Option(title="Part of Speech Selector", score=100)] + [
                    Option(title=pos, callback="change_query", params=[f"{word}!{pos}"])
                    for pos in parts_of_speech
                ]
            if filter_query == "syllables":
                syllables = self.get_syllables(word)
                return [Option(title="-".join(syllables))] or self.handle_wnf(word)
            elif filter_query == "similiar":
                return self.get_word_relationships(word) or self.handle_wnf(word)
            elif filter_query.startswith("rel-"):
                rel_type = filter_query.removeprefix("rel-")
                relationships = self.get_word_relationships(word)
                for relationship in relationships:
                    if relationship.type == rel_type:
                        return relationship.get_word_options() or self.handle_wnf(word)

        definitions = self.get_definitions(word)

        if filter_query:
            if filter_query in parts_of_speech:
                temp = filter_query.replace("-", " ")
                definitions = filter(lambda d: d.part_of_speech == temp, definitions)
            else:
                return [
                    Option(
                        title="Unknown Search Modifier Given",
                        sub="Press ENTER to open a select modifier menu.",
                        callback="change_query",
                        params=[f"{word}!select-modifier"],
                        icon="error",
                        context_data=[
                            Option(
                                title="Open Search Modifier section",
                                callback="open_url",
                                params=[
                                    "https://github.com/cibere/Flow.Launcher.Plugin.WordNikDictionary?tab=readme-ov-file#search-modifiers"
                                ],
                                sub="Press ENTER to open search modifier index",
                            )
                        ],
                    )
                ]

        return definitions or self.handle_wnf(word)

    def context_menu(self, data: list[Any]):
        LOG.debug(f"Context menu received: {data=}")
        return data

    def open_url(self, url):
        webbrowser.open(url)

    def open_settings_menu(self):
        FlowLauncherAPI.open_setting_dialog()

    def change_query(self, query: str):
        with open("plugin.json", "r") as f:
            data = json.load(f)
        FlowLauncherAPI.change_query(f"{data['ActionKeyword']} {query}")

    def open_log_file_folder(self):
        os.system(f'explorer.exe /select, "wordnik.logs"')

    def download_word_list(self):
        data: bytes = self.http.fetch_word_list_file()
        with open(DEFAULT_WORD_LIST_LOC, "wb") as f:
            f.write(data)
        FlowLauncherAPI.show_msg(
            title="Word List Successfully Downloaded",
            sub_title="",
            ico_path="Images/app.png",
        )
