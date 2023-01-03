# encoding: utf-8
import json
import xml.etree.ElementTree as ET
from functools import partial
from pathlib import PurePosixPath
from urllib.parse import unquote_plus

from .credential import Credentials, AsyncCredentials
from .item import AsyncItem, Item, append_slash, snake
from .mix import (AsyncConfigurationMixIn, AsyncDeletionMixIn, AsyncDescriptionMixIn, AsyncEnableMixIn, ConfigurationMixIn, DeletionMixIn, DescriptionMixIn,
                  EnableMixIn)
from .queue import QueueItem
from .view import Views


class NameMixIn:
    # pylint: disable=no-member
    @property
    def name(self):
        return self.full_name.split('/')[-1]

    @property
    def full_name(self):
        return unquote_plus(self.jenkins._url2name(self.url))

    @property
    def full_display_name(self):
        return unquote_plus(self.full_name.replace('/', ' » '))


class Job(Item, ConfigurationMixIn, DescriptionMixIn, DeletionMixIn, NameMixIn):

    def move(self, path):
        path = path.strip('/')
        params = {'destination': f'/{path}',
                  'json': json.dumps({'destination': f'/{path}'})}
        resp = self.handle_req('POST', 'move/move', data=params)
        self.url = resp.headers['Location']
        return resp

    def rename(self, name):
        resp = self.handle_req('POST', 'confirmRename',
                               params={'newName': name})
        self.url = append_slash(resp.headers['Location'])
        return resp

    def duplicate(self, path, recursive=False):
        self.jenkins.create_job(path, self.configure(), recursive=recursive)

    @property
    def parent(self):
        path = PurePosixPath(self.full_name)
        if path.parent.name == '':
            return self.jenkins
        return self.jenkins.get_job(str(path.parent))


class Folder(Job):

    def create(self, name, xml):
        return self.handle_req('POST', 'createItem', params={'name': name},
                               headers=self.headers, content=xml)

    def get(self, name):
        for item in self.api_json(tree='jobs[name,url]')['jobs']:
            if name == item['name']:
                return self._new_instance_by_item(__name__, item)
        return None

    def iter(self, depth=0):
        query = 'jobs[url]'
        query_format = 'jobs[url,%s]'
        for _ in range(int(depth)):
            query = query_format % query

        def _resolve(item):
            yield self._new_instance_by_item(__name__, item)
            jobs = item.get('jobs')
            if jobs:
                for job in jobs:
                    yield from _resolve(job)

        for item in self.api_json(tree=query)['jobs']:
            yield from _resolve(item)

    def copy(self, src, dest):
        params = {'name': dest, 'mode': 'copy', 'from': src}
        return self.handle_req('POST', 'createItem', params=params)

    def reload(self):
        return self.handle_req('POST', 'reload')

    @property
    def views(self):
        return Views(self)

    @property
    def credentials(self):
        return Credentials(self.jenkins,
                           f'{self.url}credentials/store/folder/domain/_/')

    def __iter__(self):
        yield from self.iter()

    def __call__(self, depth):
        yield from self.iter(depth)

    def __getitem__(self, name):
        return self.get(name)


class WorkflowMultiBranchProject(Folder, EnableMixIn):

    def scan(self, delay=0):
        return self.handle_req('POST', 'build', params={'delay': delay})

    def get_scan_log(self):
        with self.handle_stream('GET', 'indexing/consoleText') as resp:
            yield from resp.iter_lines()

    @property
    def buildable(self):
        return ET.XML(self.configure()).find('disabled').text == 'false'


class OrganizationFolder(WorkflowMultiBranchProject):
    pass


class Project(Job, EnableMixIn):

    def __init__(self, jenkins, url):
        super().__init__(jenkins, url)

        def _get_build_by_key(key):
            item = self.api_json(tree=f'{key}[url]')[key]
            if item is None:
                return None
            return self._new_instance_by_item('api4jenkins.build', item)

        for key in ['firstBuild', 'lastBuild', 'lastCompletedBuild',
                    'lastFailedBuild', 'lastStableBuild', 'lastUnstableBuild',
                    'lastSuccessfulBuild', 'lastUnsuccessfulBuild']:
            setattr(self, snake(f'get_{key}'),
                    partial(_get_build_by_key, key))

    def build(self, **params):
        reserved = ['token', 'delay']
        if not params or all(k in reserved for k in params):
            entry = 'build'
        else:
            entry = 'buildWithParameters'
        resp = self.handle_req('POST', entry, params=params)
        return QueueItem(self.jenkins, resp.headers['Location'])

    def get_build(self, number):
        for item in self.api_json(tree='builds[number,displayName,url]')['builds']:
            if number == item['number'] or number == item['displayName']:
                return self._new_instance_by_item('api4jenkins.build', item)
        return None

    def iter_builds(self):
        yield from self

    def iter_all_builds(self):
        for item in self.api_json(tree='allBuilds[number,url]')['allBuilds']:
            yield self._new_instance_by_item('api4jenkins.build', item)

    def set_next_build_number(self, number):
        self.handle_req('POST', 'nextbuildnumber/submit',
                        params={'nextBuildNumber': number})

    def get_parameters(self):
        params = []
        for p in self.api_json()['property']:
            if 'parameterDefinitions' in p:
                params = p['parameterDefinitions']
        return params

    @property
    def building(self):
        builds = self.api_json(tree='builds[building]')['builds']
        return any(b['building'] for b in builds)

    def __iter__(self):
        for item in self.api_json(tree='builds[number,url]')['builds']:
            yield self._new_instance_by_item('api4jenkins.build', item)

    def __getitem__(self, number):
        return self.get_build(number)

    def filter_builds_by_result(self, *, result):
        """filter build by build results, avaliable results are:
        'SUCCESS', 'UNSTABLE', 'FAILURE', 'NOT_BUILT', 'ABORTED'
        see: https://javadoc.jenkins-ci.org/hudson/model/Result.html
        """
        expect = ['SUCCESS', 'UNSTABLE', 'FAILURE', 'NOT_BUILT', 'ABORTED']
        if result not in expect:
            raise ValueError(f'Expect one of {expect}')
        yield from filter(lambda build: build.result == result, self)


class WorkflowJob(Project):
    pass


class MatrixProject(Project):
    pass


class FreeStyleProject(Project):
    pass


class MavenModuleSet(Project):
    pass


class ExternalJob(Project):
    pass


class MultiJobProject(Project):
    pass


class IvyModuleSet(Project):
    pass


class BitbucketSCMNavigator(Project):
    pass


class GitHubSCMNavigator(Project):
    pass


class PipelineMultiBranchDefaultsProject(Project):
    pass

# async class


class AsyncJob(AsyncItem, AsyncConfigurationMixIn, AsyncDescriptionMixIn, AsyncDeletionMixIn, NameMixIn):

    async def move(self, path):
        path = path.strip('/')
        params = {'destination': f'/{path}',
                  'json': json.dumps({'destination': f'/{path}'})}
        resp = await self.handle_req('POST', 'move/move', data=params)
        self.url = resp.headers['Location']
        return resp

    async def rename(self, name):
        resp = await self.handle_req('POST', 'confirmRename',
                                     params={'newName': name})
        self.url = append_slash(resp.headers['Location'])
        return resp

    async def duplicate(self, path, recursive=False):
        await self.jenkins.create_job(path, self.configure(), recursive=recursive)

    @property
    async def parent(self):
        path = PurePosixPath(self.full_name)
        if path.parent.name == '':
            return self.jenkins
        return await self.jenkins.get_job(str(path.parent))


class AsyncFolder(AsyncJob):

    async def create(self, name, xml):
        return await self.handle_req('POST', 'createItem', params={'name': name},
                                     headers=self.headers, content=xml)

    async def get(self, name):
        resp = await self.api_json(tree='jobs[name,url]')
        for item in resp['jobs']:
            if name == item['name']:
                return self._new_instance_by_item(__name__, item)
        return None

    async def iter(self, depth=0):
        query = 'jobs[url]'
        query_format = 'jobs[url,%s]'
        for _ in range(int(depth)):
            query = query_format % query

        async def _resolve(item):
            yield self._new_instance_by_item(__name__, item)
            jobs = item.get('jobs')
            if not jobs:
                return
            for job in jobs:
                async for child in _resolve(job):
                    yield child

        for item in (await self.api_json(tree=query))['jobs']:
            async for job in _resolve(item):
                yield job

    async def copy(self, src, dest):
        params = {'name': dest, 'mode': 'copy', 'from': src}
        return await self.handle_req('POST', 'createItem', params=params)

    async def reload(self):
        return await self.handle_req('POST', 'reload')

    @property
    def views(self):
        return Views(self)

    @property
    def credentials(self):
        return AsyncCredentials(self.jenkins,
                                f'{self.url}credentials/store/folder/domain/_/')

    async def __aiter__(self):
        async for item in self.iter():
            yield item

    async def __call__(self, depth):
        async for job in self.iter(depth):
            yield job

    async def __getitem__(self, name):
        return await self.get(name)


class AsyncWorkflowMultiBranchProject(AsyncFolder, AsyncEnableMixIn):

    async def scan(self, delay=0):
        return await self.handle_req('POST', 'build', params={'delay': delay})

    async def get_scan_log(self):
        async with self.handle_stream('GET', 'indexing/consoleText') as resp:
            async for line in resp.iter_lines():
                yield line

    @property
    async def buildable(self):
        return ET.XML(await self.configure()).find('disabled').text == 'false'


class AsyncOrganizationFolder(AsyncWorkflowMultiBranchProject):
    pass


class AsyncProject(AsyncJob, AsyncEnableMixIn):

    def __init__(self, jenkins, url):
        super().__init__(jenkins, url)

        async def _get_build_by_key(key):
            item = self.api_json(tree=f'{key}[url]')[key]
            if item is None:
                return None
            return self._new_instance_by_item('api4jenkins.build', item)

        for key in ['firstBuild', 'lastBuild', 'lastCompletedBuild',
                    'lastFailedBuild', 'lastStableBuild', 'lastUnstableBuild',
                    'lastSuccessfulBuild', 'lastUnsuccessfulBuild']:
            setattr(self, snake(f'get_{key}'),
                    partial(_get_build_by_key, key))

    async def build(self, **params):
        reserved = ['token', 'delay']
        if not params or all(k in reserved for k in params):
            entry = 'build'
        else:
            entry = 'buildWithParameters'
        resp = await self.handle_req('POST', entry, params=params)
        return QueueItem(self.jenkins, resp.headers['Location'])

    async def get_build(self, number):
        async for item in self.api_json(tree='builds[number,displayName,url]')['builds']:
            if number in [item['number'], item['displayName']]:
                return self._new_instance_by_item('api4jenkins.build', item)
        return None

    async def iter_builds(self):
        for build in self:
            yield build

    async def iter_all_builds(self):
        async for item in self.api_json(tree='allBuilds[number,url]')['allBuilds']:
            yield self._new_instance_by_item('api4jenkins.build', item)

    async def set_next_build_number(self, number):
        await self.handle_req('POST', 'nextbuildnumber/submit',
                              params={'nextBuildNumber': number})

    async def get_parameters(self):
        params = []
        async for p in self.api_json()['property']:
            if 'parameterDefinitions' in p:
                params = p['parameterDefinitions']
        return params

    @property
    async def building(self):
        builds = self.api_json(tree='builds[building]')['builds']
        return any(b['building'] for b in builds)

    async def __aiter__(self):
        async for item in self.api_json(tree='builds[number,url]')['builds']:
            yield self._new_instance_by_item('api4jenkins.build', item)

    async def __getitem__(self, number):
        return self.get_build(number)

    async def filter_builds_by_result(self, *, result):
        """filter build by build results, avaliable results are:
        'SUCCESS', 'UNSTABLE', 'FAILURE', 'NOT_BUILT', 'ABORTED'
        see: https://javadoc.jenkins-ci.org/hudson/model/Result.html
        """
        expect = ['SUCCESS', 'UNSTABLE', 'FAILURE', 'NOT_BUILT', 'ABORTED']
        if result not in expect:
            raise ValueError(f'Expect one of {expect}')
        async for build in self:
            if await build.result == result:
                yield build


class AsyncWorkflowJob(AsyncProject):
    pass


class AsyncMatrixProject(AsyncProject):
    pass


class AsyncFreeStyleProject(AsyncProject):
    pass


class AsyncMavenModuleSet(AsyncProject):
    pass


class AsyncExternalJob(AsyncProject):
    pass


class AsyncMultiJobProject(AsyncProject):
    pass


class AsyncIvyModuleSet(AsyncProject):
    pass


class AsyncBitbucketSCMNavigator(AsyncProject):
    pass


class AsyncGitHubSCMNavigator(AsyncProject):
    pass


class AsyncPipelineMultiBranchDefaultsProject(AsyncProject):
    pass
