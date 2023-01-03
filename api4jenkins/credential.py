# encoding: utf-8


from .item import Item, AsyncItem
from .mix import ConfigurationMixIn, DeletionMixIn, AsyncConfigurationMixIn, AsyncDeletionMixIn


class Credentials(Item):

    def get(self, id):
        for item in self.api_json(tree='credentials[id]')['credentials']:
            if item['id'] == id:
                return Credential(self.jenkins,
                                  f'{self.url}credential/{id}/')
        return None

    def create(self, xml):
        self.handle_req('POST', 'createCredentials',
                        headers=self.headers, content=xml)

    def __iter__(self):
        for item in self.api_json(tree='credentials[id]')['credentials']:
            yield Credential(self.jenkins,
                             f'{self.url}credential/{item["id"]}/')


class Credential(Item, ConfigurationMixIn, DeletionMixIn):
    pass


# async class

class AsyncCredentials(AsyncItem):

    async def get(self, id):
        for item in (await self.api_json(tree='credentials[id]'))['credentials']:
            if item['id'] == id:
                return AsyncCredential(self.jenkins,
                                       f'{self.url}credential/{id}/')
        return None

    async def create(self, xml):
        await self.handle_req('POST', 'createCredentials',
                              headers=self.headers, content=xml)

    async def __aiter__(self):
        for item in (await self.api_json(tree='credentials[id]'))['credentials']:
            yield AsyncCredential(self.jenkins,
                                  f'{self.url}credential/{item["id"]}/')


class AsyncCredential(AsyncItem, AsyncConfigurationMixIn, AsyncDeletionMixIn):
    pass
