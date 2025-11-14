# encoding: utf-8


from .item import AsyncItem, Item
from .mix import (AsyncConfigurationMixIn, AsyncDeletionMixIn,
                  ConfigurationMixIn, DeletionMixIn)


class Credentials(Item):

    def get(self, name):
        for key in self.api_json(tree='domains[urlName]')['domains'].keys():
            if key == name:
                return Domain(self.jenkins, f'{self.url}domain/{key}/')
        return None

    def create(self, xml):
        self.handle_req('POST', 'createDomain',
                        headers=self.headers, content=xml)

    def iter(self):
        for key in self.api_json(tree='domains[urlName]')['domains'].keys():
            yield Domain(self.jenkins, f'{self.url}domain/{key}/')

    @property
    def global_domain(self):
        return self['_']


class Domain(Item, ConfigurationMixIn, DeletionMixIn):

    def get(self, id):
        for item in self.api_json(tree='credentials[id]')['credentials']:
            if item['id'] == id:
                return Credential(self.jenkins, f'{self.url}credential/{id}/')
        return None

    def create(self, xml):
        self.handle_req('POST', 'createCredentials',
                        headers=self.headers, content=xml)

    def iter(self):
        for item in self.api_json(tree='credentials[id]')['credentials']:
            yield Credential(self.jenkins, f'{self.url}credential/{item["id"]}/')


class Credential(Item, ConfigurationMixIn, DeletionMixIn):
    pass


# async class
class AsyncCredentials(AsyncItem):

    async def get(self, name):
        data = await self.api_json(tree='domains[urlName]')
        for key in data['domains'].keys():
            if key == name:
                return AsyncDomain(self.jenkins, f'{self.url}domain/{key}/')
        return None

    async def create(self, xml):
        await self.handle_req('POST', 'createDomain',
                              headers=self.headers, content=xml)

    async def aiter(self):
        data = await self.api_json(tree='domains[urlName]')
        for key in data['domains'].keys():
            yield Domain(self.jenkins, f'{self.url}domain/{key}/')

    @property
    async def global_domain(self):
        return await self['_']


class AsyncDomain(AsyncItem, AsyncConfigurationMixIn, AsyncDeletionMixIn):

    async def get(self, id):
        data = await self.api_json(tree='credentials[id]')
        for item in data['credentials']:
            if item['id'] == id:
                return AsyncCredential(self.jenkins, f'{self.url}credential/{id}/')
        return None

    async def create(self, xml):
        await self.handle_req('POST', 'createCredentials',
                              headers=self.headers, content=xml)

    async def aiter(self):
        data = await self.api_json(tree='credentials[id]')
        for item in data['credentials']:
            yield AsyncCredential(self.jenkins, f'{self.url}credential/{item["id"]}/')


class AsyncCredential(AsyncItem, AsyncConfigurationMixIn, AsyncDeletionMixIn):
    pass
