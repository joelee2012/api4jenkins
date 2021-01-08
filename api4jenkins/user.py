# encoding: utf-8
from collections import namedtuple

from .item import Item


class Users(Item):
    def __iter__(self):
        for user in self.api_json()['users']:
            yield User(self.jenkins, user['user']['absoluteUrl'])


ApiToken = namedtuple('ApiToken', ['name', 'uuid', 'value'])


class User(Item):

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
