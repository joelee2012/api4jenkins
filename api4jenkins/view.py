# encoding: utf-8

from .item import Item
from .mix import ConfigrationMix, DeletionMix


class Views(Item):
    '''
    classdocs
    '''

    def __init__(self, provider):
        '''
        Constructor
        '''
        self.provider = provider
        super().__init__(provider.jenkins, provider.url)

    def get(self, name):
        for item in self.api_json(tree='views[name,url]')['views']:
            if name == item['name']:
                return self._new_instance_by_item(__name__, item)
        return None

    def create(self, name, xml):
        self.handle_req('POST', 'createView', params={'name': name},
                        headers=self.headers, data=xml)

    def __iter__(self):
        for item in self.api_json(tree='views[name,url]')['views']:
            yield self._new_instance_by_item(__name__, item)


class View(Item, ConfigrationMix, DeletionMix):

    def get_job(self, name):
        for item in self.api_json(tree='jobs[name,url]')['jobs']:
            if name == item['name']:
                return self._new_instance_by_item('api4jenkins.job', item)
        return None

    def __iter__(self):
        for item in self.api_json(tree='jobs[name,url]')['jobs']:
            yield self._new_instance_by_item('api4jenkins.job', item)

    def include(self, name):
        self.handle_req('POST', 'addJobToView', params={'name': name})

    def exclude(self, name):
        self.handle_req('POST', 'removeJobFromView', params={'name': name})


class AllView(View):
    pass


class MyView(View):
    pass


class ListView(View):
    pass
