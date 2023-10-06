# encoding: utf-8

from .item import AsyncItem, Item
from .mix import (AsyncConfigurationMixIn, AsyncDeletionMixIn,
                  AsyncDescriptionMixIn, ConfigurationMixIn,
                  DeletionMixIn, DescriptionMixIn)


class Views(Item):
    '''
    classdocs
    '''

    def __init__(self, owner):
        '''
        Constructor
        '''
        self.owner = owner
        super().__init__(owner.jenkins, owner.url)

    def get(self, name):
        for item in self.api_json(tree='views[name,url]')['views']:
            if name == item['name']:
                return self._new_item(__name__, item)
        return None

    def create(self, name, xml):
        self.handle_req('POST', 'createView', params={'name': name},
                        headers=self.headers, content=xml)

    def __iter__(self):
        for item in self.api_json(tree='views[name,url]')['views']:
            yield self._new_item(__name__, item)


class View(Item, ConfigurationMixIn, DescriptionMixIn, DeletionMixIn):

    def get(self, name):
        for item in self.api_json(tree='jobs[name,url]')['jobs']:
            if name == item['name']:
                return self._new_item('api4jenkins.job', item)
        return None

    def __iter__(self):
        for item in self.api_json(tree='jobs[name,url]')['jobs']:
            yield self._new_item('api4jenkins.job', item)

    def include(self, name):
        self.handle_req('POST', 'addJobToView', params={'name': name})

    def exclude(self, name):
        self.handle_req('POST', 'removeJobFromView', params={'name': name})


class AllView(View):
    def __init__(self, jenkins, url):
        # name of all view for jenkins is 'all', but for folder is 'All'
        name = 'view/all' if jenkins.url == url else 'view/All'
        super().__init__(jenkins, url + name)


class MyView(View):
    pass


class ListView(View):
    pass


class Dashboard(View):
    pass


class NestedView(View):

    @property
    def views(self):
        return Views(self)


class SectionedView(View):
    pass


class AsyncViews(AsyncItem):
    '''
    classdocs
    '''

    def __init__(self, owner):
        '''
        Constructor
        '''
        self.owner = owner
        super().__init__(owner.jenkins, owner.url)

    async def get(self, name):
        data = await self.api_json(tree='views[name,url]')
        for item in data['views']:
            if name == item['name']:
                return self._new_item(__name__, item)
        return None

    async def create(self, name, xml):
        await self.handle_req('POST', 'createView', params={'name': name},
                              headers=self.headers, content=xml)

    async def __aiter__(self):
        data = await self.api_json(tree='views[name,url]')
        for item in data['views']:
            yield self._new_item(__name__, item)


class AsyncView(AsyncItem, AsyncConfigurationMixIn, AsyncDescriptionMixIn, AsyncDeletionMixIn):

    async def get(self, name):
        data = await self.api_json(tree='jobs[name,url]')
        for item in data['jobs']:
            if name == item['name']:
                return self._new_item('api4jenkins.job', item)
        return None

    async def __aiter__(self):
        data = await self.api_json(tree='jobs[name,url]')
        for item in data['jobs']:
            yield self._new_item('api4jenkins.job', item)

    async def include(self, name):
        await self.handle_req('POST', 'addJobToView', params={'name': name})

    async def exclude(self, name):
        await self.handle_req('POST', 'removeJobFromView', params={'name': name})


class AsyncAllView(AsyncView):
    def __init__(self, jenkins, url):
        # name of all view for jenkins is 'all', but for folder is 'All'
        name = 'view/all' if jenkins.url == url else 'view/All'
        super().__init__(jenkins, url + name)


class AsyncMyView(AsyncView):
    pass


class AsyncListView(AsyncView):
    pass


class AsyncDashboard(AsyncView):
    pass


class AsyncNestedView(AsyncView):

    @property
    def views(self):
        return AsyncViews(self)


class AsyncSectionedView(AsyncView):
    pass
