# encoding: utf-8

import json

from .exceptions import ItemNotFoundError
from .item import Item, new_item, AsyncItem
from .mix import ConfigurationMixIn, DeletionMixIn, RunScriptMixIn, AsyncConfigurationMixIn, AsyncDeletionMixIn, AsyncRunScriptMixIn


class IterBuildingBuildsMixIn:
    # pylint: disable=no-member
    def iter_building_builds(self):
        yield from filter(lambda build: build.building, self.iter_builds())


class Nodes(Item, IterBuildingBuildsMixIn):
    '''
    classdocs
    '''

    def create(self, name, **kwargs):
        node_setting = {
            'nodeDescription': '',
            'numExecutors': 1,
            'remoteFS': '/home/jenkins',
            'labelString': '',
            'mode': 'NORMAL',
            'retentionStrategy': {
                'stapler-class': 'hudson.slaves.RetentionStrategy$Always'
            },
            'nodeProperties': {'stapler-class-bag': 'true'},
            'launcher': {'stapler-class': 'hudson.slaves.JNLPLauncher'}
        }
        node_setting.update(kwargs)
        params = {
            'name': name,
            'type': 'hudson.slaves.DumbSlave$DescriptorImpl',
            'json': json.dumps(node_setting)
        }
        self.handle_req('POST', 'doCreateItem', data=params)

    def get(self, name):
        for item in self.api_json(tree='computer[displayName]')['computer']:
            if name == item['displayName']:
                item['url'] = f"{self.url}{item['displayName']}/"
                return self._new_instance_by_item(__name__, item)
        return None

    def iter_builds(self):
        builds = {}
        # iterate 'executors', 'oneOffExecutors' in order,
        # cause freestylebuild is in executors, and _class of workflowbuild in
        # executors is PlaceholderExecutable
        tree = ('computer[executors[currentExecutable[url]],'
                'oneOffExecutors[currentExecutable[url]]]')
        for computer in self.api_json(tree, 2)['computer']:
            _parse_builds(computer, builds)

        yield from _new_items(self.jenkins, builds)

    def __iter__(self):
        for item in self.api_json(tree='computer[displayName]')['computer']:
            item['url'] = f"{self.url}{item['displayName']}/"
            yield self._new_instance_by_item(__name__, item)

    def filter_node_by_label(self, *labels):
        for node in self:
            for label in node.api_json()['assignedLabels']:
                if label['name'] in labels:
                    yield node

    def filter_node_by_status(self, *, online):
        yield from filter(lambda node: online != node.offline, self)

# following two functions should be used in this module only


def _new_items(jenkins, builds):
    for url, class_name in builds.items():
        item = {'url': url, '_class': class_name}
        yield new_item(jenkins, 'api4jenkins.build', item)


def _parse_builds(data, builds):
    for kind in ['executors', 'oneOffExecutors']:
        for executor in data.get(kind):
            # in case of issue:
            # https://github.com/joelee2012/api4jenkins/issues/16
            execable = executor['currentExecutable']
            if not execable:
                continue
            if execable['_class'].endswith('PlaceholderExecutable'):
                execable['_class'] = 'org.jenkinsci.plugins.workflow.job.WorkflowRun'
            builds[execable['url']] = execable['_class']


class Node(Item, ConfigurationMixIn, DeletionMixIn, RunScriptMixIn):

    def enable(self):
        if self.offline:
            self.handle_req('POST', 'toggleOffline',
                            params={'offlineMessage': ''})

    def disable(self, msg=''):
        if not self.offline:
            self.handle_req('POST', 'toggleOffline',
                            params={'offlineMessage': msg})

    def iter_builds(self):
        builds = {}
        # iterate 'executors', 'oneOffExecutors' in order,
        # cause freestylebuild is in executors
        tree = ('executors[currentExecutable[url]],'
                'oneOffExecutors[currentExecutable[url]]')
        _parse_builds(self.api_json(tree, 2), builds)
        yield from _new_items(self.jenkins, builds)

    def __iter__(self):
        yield from self.iter_builds()


class MasterComputer(Node):
    def __init__(self, jenkins, url):
        # rename built-in node: https://www.jenkins.io/doc/upgrade-guide/2.319/
        name = 'master' if url.endswith('/master/') else 'built-in'
        super().__init__(jenkins, f'{jenkins.url}computer/({name})/')


class SlaveComputer(Node):
    pass


class KubernetesComputer(Node):

    def exists(self):
        try:
            self.handle_req('GET', '')
            return True
        except ItemNotFoundError:
            return False


class DockerComputer(Node):
    pass


class EC2Computer(Node):
    pass


class AsyncIterBuildingBuildsMixIn:
    # pylint: disable=no-member
    async def iter_building_builds(self):
        async for build in self.iter_builds():
            if await build.building:
                yield build


class AsyncNodes(AsyncItem, AsyncIterBuildingBuildsMixIn):
    '''
    classdocs
    '''

    async def create(self, name, **kwargs):
        node_setting = {
            'nodeDescription': '',
            'numExecutors': 1,
            'remoteFS': '/home/jenkins',
            'labelString': '',
            'mode': 'NORMAL',
            'retentionStrategy': {
                'stapler-class': 'hudson.slaves.RetentionStrategy$Always'
            },
            'nodeProperties': {'stapler-class-bag': 'true'},
            'launcher': {'stapler-class': 'hudson.slaves.JNLPLauncher'}
        }
        node_setting.update(kwargs)
        params = {
            'name': name,
            'type': 'hudson.slaves.DumbSlave$DescriptorImpl',
            'json': json.dumps(node_setting)
        }
        await self.handle_req('POST', 'doCreateItem', data=params)

    async def get(self, name):
        data = await self.api_json(tree='computer[displayName]')
        for item in data['computer']:
            if name == item['displayName']:
                item['url'] = f"{self.url}{item['displayName']}/"
                return self._new_instance_by_item(__name__, item)
        return None

    async def iter_builds(self):
        builds = {}
        # iterate 'executors', 'oneOffExecutors' in order,
        # cause freestylebuild is in executors, and _class of workflowbuild in
        # executors is PlaceholderExecutable
        tree = ('computer[executors[currentExecutable[url]],'
                'oneOffExecutors[currentExecutable[url]]]')
        data = await self.api_json(tree, 2)
        for computer in data['computer']:
            _parse_builds(computer, builds)
        for build in _new_items(self.jenkins, builds):
            yield build

    async def __aiter__(self):
        data = await self.api_json(tree='computer[displayName]')
        for item in data['computer']:
            item['url'] = f"{self.url}{item['displayName']}/"
            yield self._new_instance_by_item(__name__, item)

    async def filter_node_by_label(self, *labels):
        async for node in self:
            data = await node.api_json()
            async for label in data['assignedLabels']:
                if label['name'] in labels:
                    yield node

    async def filter_node_by_status(self, *, online):
        async for node in self:
            if online != await node.offline:
                yield node


class AsyncNode(AsyncItem, AsyncConfigurationMixIn, AsyncDeletionMixIn, AsyncRunScriptMixIn, AsyncIterBuildingBuildsMixIn):

    async def enable(self):
        if await self.offline:
            await self.handle_req('POST', 'toggleOffline',
                                  params={'offlineMessage': ''})

    async def disable(self, msg=''):
        if not await self.offline:
            await self.handle_req('POST', 'toggleOffline',
                                  params={'offlineMessage': msg})

    async def iter_builds(self):
        builds = {}
        # iterate 'executors', 'oneOffExecutors' in order,
        # cause freestylebuild is in executors
        tree = ('executors[currentExecutable[url]],'
                'oneOffExecutors[currentExecutable[url]]')
        _parse_builds(await self.api_json(tree, 2), builds)
        for build in _new_items(self.jenkins, builds):
            yield build

    async def __aiter__(self):
        async for build in self.iter_builds():
            yield build


class AsyncMasterComputer(AsyncNode):
    def __init__(self, jenkins, url):
        # rename built-in node: https://www.jenkins.io/doc/upgrade-guide/2.319/
        name = 'master' if url.endswith('/master/') else 'built-in'
        super().__init__(jenkins, f'{jenkins.url}computer/({name})/')


class AsyncSlaveComputer(AsyncNode):
    pass


class AsyncKubernetesComputer(AsyncNode):

    async def exists(self):
        try:
            await self.handle_req('GET', '')
            return True
        except ItemNotFoundError:
            return False


class AsyncDockerComputer(AsyncNode):
    pass


class AsyncEC2Computer(AsyncNode):
    pass
