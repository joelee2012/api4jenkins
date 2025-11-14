# encoding: utf-8

from typing import Any, Dict, Iterator, AsyncIterator, Optional
from .item import AsyncItem, Item
from .mix import (AsyncConfigurationMixIn, AsyncDeletionMixIn,
                  ConfigurationMixIn, DeletionMixIn)
from httpx import Response


class Credentials(Item):

    def get(self, name: str) -> Optional['Domain']:
        for key in self.api_json(tree='domains[urlName]')['domains'].keys():
            if key == name:
                return Domain(self.jenkins, f'{self.url}domain/{key}/')
        return None

    def create(self, xml: str) -> Response:
        return self.handle_req('POST', 'createDomain',
                             headers=self.headers, content=xml)

    def iter(self) -> Iterator['Domain']:  # type: ignore[override]
        """Override Item.iter() to provide domain iteration.
        Note: This intentionally changes the return type from None to Iterator."""
        for key in self.api_json(tree='domains[urlName]')['domains'].keys():
            yield Domain(self.jenkins, f'{self.url}domain/{key}/')

    @property
    def global_domain(self) -> 'Domain':
        domain = self['_']
        assert domain is not None
        return domain


class Domain(Item, ConfigurationMixIn, DeletionMixIn):

    def get(self, id: str) -> Optional['Credential']:
        for item in self.api_json(tree='credentials[id]')['credentials']:
            if item['id'] == id:
                return Credential(self.jenkins, f'{self.url}credential/{id}/')
        return None

    def create(self, xml: str) -> Response:
        return self.handle_req('POST', 'createCredentials',
                             headers=self.headers, content=xml)

    def iter(self) -> Iterator['Credential']:  # type: ignore[override]
        """Override Item.iter() to provide credential iteration.
        Note: This intentionally changes the return type from None to Iterator."""
        for item in self.api_json(tree='credentials[id]')['credentials']:
            yield Credential(self.jenkins, f'{self.url}credential/{item["id"]}/')


class Credential(Item, ConfigurationMixIn, DeletionMixIn):
    pass


# async class
class AsyncCredentials(AsyncItem):

    async def get(self, name: str) -> Optional['AsyncDomain']:
        data = await self.api_json(tree='domains[urlName]')
        for key in data['domains'].keys():
            if key == name:
                return AsyncDomain(self.jenkins, f'{self.url}domain/{key}/')
        return None

    async def create(self, xml: str) -> Response:
        return await self.handle_req('POST', 'createDomain',
                                   headers=self.headers, content=xml)

    async def aiter(self) -> AsyncIterator['AsyncDomain']:  # type: ignore[override]
        """Override AsyncItem.aiter() to provide async domain iteration.
        Note: This intentionally changes the return type from None to AsyncIterator."""
        data = await self.api_json(tree='domains[urlName]')
        for key in data['domains'].keys():
            yield AsyncDomain(self.jenkins, f'{self.url}domain/{key}/')

    @property
    async def global_domain(self) -> 'AsyncDomain':
        domain = await self['_']
        assert domain is not None
        return domain


class AsyncDomain(AsyncItem, AsyncConfigurationMixIn, AsyncDeletionMixIn):

    async def get(self, id: str) -> Optional['AsyncCredential']:
        data = await self.api_json(tree='credentials[id]')
        for item in data['credentials']:
            if item['id'] == id:
                return AsyncCredential(self.jenkins, f'{self.url}credential/{id}/')
        return None

    async def create(self, xml: str) -> Response:
        return await self.handle_req('POST', 'createCredentials',
                                   headers=self.headers, content=xml)

    async def aiter(self) -> AsyncIterator['AsyncCredential']:  # type: ignore[override]
        """Override AsyncItem.aiter() to provide async credential iteration.
        Note: This intentionally changes the return type from None to AsyncIterator."""
        data = await self.api_json(tree='credentials[id]')
        for item in data['credentials']:
            yield AsyncCredential(self.jenkins, f'{self.url}credential/{item["id"]}/')


class AsyncCredential(AsyncItem, AsyncConfigurationMixIn, AsyncDeletionMixIn):
    pass
