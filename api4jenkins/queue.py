# encoding: utf-8
import re

from .item import AsyncItem, Item
from .mix import (ActionsMixIn, AsyncActionsMixIn)


class Queue(Item):
    def get(self, id):
        for item in self.api_json(tree='items[id,url]')['items']:
            if item['id'] == int(id):
                return QueueItem(self.jenkins,
                                 f"{self.jenkins.url}{item['url']}")
        return None

    def cancel(self, id):
        self.handle_req('POST', 'cancelItem', params={'id': id})

    def __iter__(self):
        for item in self.api_json(tree='items[url]')['items']:
            yield QueueItem(self.jenkins, f"{self.jenkins.url}{item['url']}")

# https://javadoc.jenkins.io/hudson/model/Queue.html#buildables
#  (enter) --> waitingList --+--> blockedProjects
#                            |        ^
#                            |        |
#                            |        v
#                            +--> buildables ---> pending ---> left
#                                     ^              |
#                                     |              |
#                                     +---(rarely)---+


class QueueItem(Item, ActionsMixIn):

    def __init__(self, jenkins, url):
        if not url.startswith('https') and jenkins.url.startswith('https'):
            url = re.sub(r'^http[s]', 'https', url)
        super().__init__(jenkins, url)
        self.id = int(self.url.split('/')[-2])
        self._build = None

    def get_job(self):
        if self._class.endswith('$BuildableItem'):
            return self.get_build().project
        task = self.api_json(tree='task[url]')['task']
        return self._new_item('api4jenkins.job', task)

    def get_build(self):
        if not self._build:
            _class = self._class
            # BlockedItem does not have build
            if _class.endswith('$LeftItem'):
                executable = self.api_json('executable[url]')['executable']
                self._build = self._new_item(
                    'api4jenkins.build', executable)
            elif _class.endswith(('$BuildableItem', '$WaitingItem')):
                for build in self.jenkins.nodes.iter_builds():
                    # https://javadoc.jenkins.io/hudson/model/Run.html#getQueueId--
                    # https://javadoc.jenkins.io/hudson/model/Queue.Item.html#getId--
                    # ensure build exists, see https://github.com/joelee2012/api4jenkins/issues/49
                    if build.exists() and int(build.queue_id) == self.id:
                        self._build = build
                        break
        return self._build

    def cancel(self):
        self.jenkins.queue.cancel(self.id)

# due to item type is dynamic


class BuildableItem(QueueItem):
    pass


class BlockedItem(QueueItem):
    pass


class LeftItem(QueueItem):
    pass


class WaitingItem(QueueItem):
    pass

# async class


class AsyncQueue(AsyncItem):

    async def get(self, id):
        for item in (await self.api_json(tree='items[id,url]'))['items']:
            if item['id'] == int(id):
                return AsyncQueueItem(self.jenkins,
                                      f"{self.jenkins.url}{item['url']}")
        return None

    async def cancel(self, id):
        await self.handle_req('POST', 'cancelItem', params={'id': id})

    async def __aiter__(self):
        for item in (await self.api_json(tree='items[url]'))['items']:
            yield AsyncQueueItem(self.jenkins, f"{self.jenkins.url}{item['url']}")


class AsyncQueueItem(AsyncItem, AsyncActionsMixIn):

    def __init__(self, jenkins, url):
        if not url.startswith('https') and jenkins.url.startswith('https'):
            url = re.sub(r'^http[s]', 'https', url)
        super().__init__(jenkins, url)
        self.id = int(self.url.split('/')[-2])
        self._build = None

    async def get_job(self):
        _class = await self._class
        if _class.endswith('$BuildableItem'):
            build = await self.get_build()
            return await build.project
        data = await self.api_json(tree='task[url]')
        return self._new_item('api4jenkins.job', data['task'])

    async def get_build(self):
        if not self._build:
            _class = await self._class
            # BlockedItem does not have build
            if _class.endswith('$LeftItem'):
                data = await self.api_json('executable[url]')
                self._build = self._new_item(
                    'api4jenkins.build', data['executable'])
            elif _class.endswith(('$BuildableItem', '$WaitingItem')):
                async for build in self.jenkins.nodes.iter_builds():
                    # https://javadoc.jenkins.io/hudson/model/Run.html#getQueueId--
                    # https://javadoc.jenkins.io/hudson/model/Queue.Item.html#getId--
                    # ensure build exists, see https://github.com/joelee2012/api4jenkins/issues/49
                    if await build.exists() and int(await build.queue_id) == self.id:
                        self._build = build
                        break
        return self._build

    async def cancel(self):
        await self.jenkins.queue.cancel(self.id)


class AsyncBuildableItem(AsyncQueueItem):
    pass


class AsyncBlockedItem(AsyncQueueItem):
    pass


class AsyncLeftItem(AsyncQueueItem):
    pass


class AsyncWaitingItem(AsyncQueueItem):
    pass
