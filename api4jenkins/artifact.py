# encoding: utf-8
import anyio
from typing import Any, Dict, Optional

from httpx import Response

from .item import AsyncItem, Item
from .mix import RawJsonMixIn


class Artifact(RawJsonMixIn, Item):

    def __init__(self, jenkins: Any, raw: Dict[str, Any]) -> None:
        super().__init__(
            jenkins, f"{jenkins.url}{raw['url'][1:]}")
        # remove trailing slash
        self.url = self.url[:-1]
        self.raw = raw
        self.raw['_class'] = 'Artifact'

    def save(self, filename: Optional[str] = None) -> None:
        if not filename:
            filename = self.name
        with self.handle_stream('GET', '') as resp:
            save_response_to(resp, filename)


def save_response_to(response: Response, filename: str) -> None:
    with open(filename, 'wb') as fd:
        for chunk in response.iter_bytes(chunk_size=128):
            fd.write(chunk)


class AsyncArtifact(RawJsonMixIn, AsyncItem):

    def __init__(self, jenkins: Any, raw: Dict[str, Any]) -> None:
        super().__init__(
            jenkins, f"{jenkins.url}{raw['url'][1:]}")
        # remove trailing slash
        self.url = self.url[:-1]
        self.raw = raw
        self.raw['_class'] = 'Artifact'

    async def save(self, filename: Optional[str] = None) -> None:
        if not filename:
            filename = self.name
        async with self.handle_stream('GET', '') as resp:
            await save_response_to(resp, filename)


async def async_save_response_to(response: Response, filename: str) -> None:
    async with anyio.wrap_file(open(filename, 'wb')) as fd:
        async for chunk in response.aiter_bytes(chunk_size=128):
            await fd.write(chunk)
