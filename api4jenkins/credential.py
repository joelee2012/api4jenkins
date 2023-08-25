# encoding: utf-8


from .item import Item
from .mix import ConfigurationMixIn, DeletionMixIn


class Credentials(Item):

    def get(self, name):
        for key in self.api_json(tree='domains[urlName]')['domains'].keys():
            if key == name:
                return Domain(self.jenkins, f'{self.url}domain/{key}/')
        return None

    def create(self, xml):
        self.handle_req('POST', 'createDomain',
                        headers=self.headers, data=xml)

    def __iter__(self):
        for key in self.api_json(tree='domains[urlName]')['domains'].keys():
            yield Domain(self.jenkins, f'{self.url}domain/{key}/')

    def __getitem__(self, name):
        return self.get(name)

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
                        headers=self.headers, data=xml)

    def __iter__(self):
        for item in self.api_json(tree='credentials[id]')['credentials']:
            yield Credential(self.jenkins, f'{self.url}credential/{item["id"]}/')

    def __getitem__(self, id):
        return self.get(id)


class Credential(Item, ConfigurationMixIn, DeletionMixIn):
    pass
