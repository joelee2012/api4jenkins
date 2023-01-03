# encoding: utf-8
from collections import namedtuple

from .item import Item, AsyncItem
from .mix import DeletionMixIn, DescriptionMixIn, AsyncDeletionMixIn, AsyncDescriptionMixIn


class Users(Item):

    tree = 'users[user[id,absoluteUrl,fullName]]'

    def __iter__(self):
        for user in self.api_json(depth=2, tree=self.tree)['users']:
            yield User(self.jenkins, user['user']['absoluteUrl'])

    def get(self, id=None, full_name=None):
        for user in self.api_json(depth=2, tree=self.tree)['users']:
            if id == user['user']['id'] or full_name == user['user']['fullName']:
                return User(self.jenkins, user['user']['absoluteUrl'])
        return None


ApiToken = namedtuple('ApiToken', ['name', 'uuid', 'value'])


class User(Item, DeletionMixIn, DescriptionMixIn):

    def generate_token(self, name=''):
        entry = 'descriptorByName/jenkins.security.' \
                'ApiTokenProperty/generateNewToken'
        data = self.handle_req('POST', entry,
                               params={'newTokenName': name}).json()['data']
        return ApiToken(data['tokenName'],
                        data['tokenUuid'], data['tokenValue'])

    def revoke_token(self, uuid):
        entry = 'descriptorByName/jenkins.security.' \
                'ApiTokenProperty/revoke'
        return self.handle_req('POST', entry,
                               params={'tokenUuid': uuid})

# async class


class AsyncUsers(AsyncItem):

    tree = 'users[user[id,absoluteUrl,fullName]]'

    async def __aiter__(self):
        for user in (await self.api_json(depth=2, tree=self.tree))['users']:
            yield AsyncUser(self.jenkins, user['user']['absoluteUrl'])

    async def get(self, id=None, full_name=None):
        for user in (await self.api_json(depth=2, tree=self.tree))['users']:
            if id == user['user']['id'] or full_name == user['user']['fullName']:
                return AsyncUser(self.jenkins, user['user']['absoluteUrl'])
        return None


ApiToken = namedtuple('ApiToken', ['name', 'uuid', 'value'])


class AsyncUser(AsyncItem, AsyncDeletionMixIn, AsyncDescriptionMixIn):

    async def generate_token(self, name=''):
        entry = 'descriptorByName/jenkins.security.' \
                'ApiTokenProperty/generateNewToken'
        data = (await self.handle_req('POST', entry,
                                      params={'newTokenName': name})).json()['data']
        return ApiToken(data['tokenName'],
                        data['tokenUuid'], data['tokenValue'])

    async def revoke_token(self, uuid):
        entry = 'descriptorByName/jenkins.security.' \
                'ApiTokenProperty/revoke'
        return await self.handle_req('POST', entry,
                                     params={'tokenUuid': uuid})
