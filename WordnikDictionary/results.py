from typing import Unpack

from flogin import ExecuteResponse, Result
from flogin.jsonrpc.results import ResultConstructorArgs


class ChangeQueryResult(Result):
    def __init__(self, new_query: str, **kwargs: Unpack[ResultConstructorArgs]) -> None:
        super().__init__(**kwargs)
        self.new_query = new_query

    async def callback(self):
        assert self.plugin

        await self.plugin.api.change_query(self.new_query)
        return ExecuteResponse(hide=False)
