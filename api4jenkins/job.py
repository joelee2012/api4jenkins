# encoding: utf-8
from _ctypes import ArgumentError
from _functools import partial
from pathlib import PurePosixPath
import json

from .credential import Credentials
from .item import snake, Item, append_slash
from .mix import ConfigrationMix, DescriptionMix, DeletionMix
from .queue import QueueItem
from .view import Views


class Job(Item, ConfigrationMix, DescriptionMix, DeletionMix):

    def move(self, path):
        path = path.strip('/')
        params = {'destination': f'/{path}',
                  'json': json.dumps({'destination': f'/{path}'})}
        resp = self.handle_req('POST', 'move/move',
                               data=params, allow_redirects=False)
        self.url = resp.headers['Location']

    def rename(self, name):
        resp = self.handle_req('POST', 'confirmRename',
                               params={'newName': name},
                               allow_redirects=False)
        self.url = append_slash(resp.headers['Location'])

    def duplicate(self, path):
        self.jenkins.create_job(path, self.configure())

    @property
    def parent(self):
        path = PurePosixPath(self.full_name)
        if path.parent.name == '':
            return self.jenkins
        return Folder(self.jenkins,
                      self.jenkins._name2url(str(path.parent)))


class Folder(Job):

    def create(self, name, xml):
        self.handle_req('POST', 'createItem', params={'name': name},
                        headers=self.headers, data=xml)

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
        self.handle_req('POST', 'createItem', params=params,
                        allow_redirects=False)

    def reload(self):
        self.handle_req('POST', 'reload')

    @property
    def views(self):
        return Views(self)

    @property
    def credentials(self):
        return Credentials(self.jenkins,
                           f'{self.url}credentials/store/folder/domain/_/')

    def __iter__(self):
        yield from self.iter_jobs()


class WorkflowMultiBranchProject(Folder):
    pass


class Project(Job):

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

    def build(self, parameters=None):
        reserved = ['token', 'delay']
        if not isinstance(parameters, (type(None), dict)):
            raise ArgumentError('Paramters should be None or Dict')
        if parameters is None or all(k in reserved for k in parameters):
            entry = 'build'
        else:
            entry = 'buildWithParameters'
        resp = self.handle_req('POST', entry, params=parameters)
        return QueueItem(self.jenkins, resp.headers['Location'])

    def get_build(self, number):
        for item in self.api_json(tree='builds[number,url]')['builds']:
            if int(number) == int(item['number']):
                return self._new_instance_by_item('api4jenkins.build', item)
        return None

    def iter_builds(self):
        yield from self

    def enable(self):
        return self.handle_req('POST', 'enable')

    def disable(self):
        return self.handle_req('POST', 'disable')

    def set_next_build_number(self, number):
        self.handle_req('POST', 'nextbuildnumber/submit',
                        params={'nextBuildNumber': number})

    @property
    def building(self):
        builds = self.api_json(tree='builds[building]')['builds']
        return any(b['building'] for b in builds)

    def __iter__(self):
        for item in self.api_json(tree='builds[number,url]')['builds']:
            yield self._new_instance_by_item('api4jenkins.build', item)


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
