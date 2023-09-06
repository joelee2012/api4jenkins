# encoding: utf-8
from collections import namedtuple

from .item import AsyncItem, Item
from .mix import (AsyncDeletionMixIn, AsyncDescriptionMixIn,
                  DeletionMixIn, DescriptionMixIn)

user_tree = 'users[user[id,absoluteUrl,fullName]]'
new_token_url = 'descriptorByName/jenkins.security.ApiTokenProperty/generateNewToken'
revoke_token_url = 'descriptorByName/jenkins.security.ApiTokenProperty/revoke'


class Users(Item):

    def __iter__(self):
        for user in self.api_json(tree=user_tree)['users']:
            yield User(self.jenkins, user['user']['absoluteUrl'])

    def get(self, name):
        for user in self.api_json(tree=user_tree)['users']:
            if name in [user['user']['id'], user['user']['fullName']]:
                return User(self.jenkins, user['user']['absoluteUrl'])
        return None


ApiToken = namedtuple('ApiToken', ['name', 'uuid', 'value'])


class User(Item, DeletionMixIn, DescriptionMixIn):

    def generate_token(self, name=''):
        data = self.handle_req('POST', new_token_url,
                               params={'newTokenName': name}).json()['data']
        return ApiToken(data['tokenName'], data['tokenUuid'], data['tokenValue'])

    def revoke_token(self, uuid):
        return self.handle_req('POST', revoke_token_url, params={'tokenUuid': uuid})

# async class


class AsyncUsers(AsyncItem):

    async def __aiter__(self):
        for user in (await self.api_json(tree=user_tree))['users']:
            yield AsyncUser(self.jenkins, user['user']['absoluteUrl'])

    async def get(self, name):
        for user in (await self.api_json(tree=user_tree))['users']:
            if name in [user['user']['id'], user['user']['fullName']]:
                return AsyncUser(self.jenkins, user['user']['absoluteUrl'])
        return None


class AsyncUser(AsyncItem, AsyncDeletionMixIn, AsyncDescriptionMixIn):

    async def generate_token(self, name=''):
        data = (await self.handle_req('POST', new_token_url,
                                      params={'newTokenName': name})).json()['data']
        return ApiToken(data['tokenName'], data['tokenUuid'], data['tokenValue'])

    async def revoke_token(self, uuid):
        return await self.handle_req('POST', revoke_token_url, params={'tokenUuid': uuid})
