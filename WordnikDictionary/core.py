from flogin import Query

from .plugin import WordnikDictionaryPlugin

plugin = WordnikDictionaryPlugin()


@plugin.search()
def get_plain_definition_handler(query: Query):
    return plugin.fetch_definitions(query.text)
