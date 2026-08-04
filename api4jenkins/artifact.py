from __future__ import annotations

from typing import Any

import anyio
from httpx import Response

from .item import AsyncItem, Item
from .mix import RawJsonMixIn


class Artifact(RawJsonMixIn, Item):

    def __init__(self, jenkins: Any, raw: dict[str, Any]) -> None:
        super().__init__(
            jenkins, f"{jenkins.url}{raw['url'][1:]}")
        # remove trailing slash
        self.url = self.url[:-1]
        self.raw = raw
        self.raw['_class'] = 'Artifact'

    def save(self, filename: str | None = None) -> None:
        if not filename:
            filename = self.name
        with self.handle_stream('GET', '') as resp:
            save_response_to(resp, filename)


def save_response_to(response: Response, filename: str) -> None:
    with open(filename, 'wb') as fd:
        fd.writelines(response.iter_bytes(chunk_size=128))


class AsyncArtifact(RawJsonMixIn, AsyncItem):

    def __init__(self, jenkins: Any, raw: dict[str, Any]) -> None:
        super().__init__(
            jenkins, f"{jenkins.url}{raw['url'][1:]}")
        # remove trailing slash
        self.url = self.url[:-1]
        self.raw = raw
        self.raw['_class'] = 'Artifact'

    async def save(self, filename: str | None = None) -> None:
        if not filename:
            filename = self.name
        async with self.handle_stream('GET', '') as resp:
            await save_response_to(resp, filename)


async def async_save_response_to(response: Response, filename: str) -> None:
    async with await anyio.open_file(filename, 'wb') as fd:
        async for chunk in response.aiter_bytes(chunk_size=128):
            await fd.write(chunk)
