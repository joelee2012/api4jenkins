# encoding: utf-8

import json

from .item import AsyncItem, Item, new_item
from .mix import (AsyncConfigurationMixIn, AsyncDeletionMixIn,
                  AsyncRunScriptMixIn, ConfigurationMixIn, DeletionMixIn,
                  RunScriptMixIn)

# query builds from 'executors', 'oneOffExecutors' in computer(s),
# cause freestylebuild is in executors, and workflowbuild has different _class in
# executors(..PlaceholderTask$PlaceholderExecutable) and oneOffExecutors(org.jenkinsci.plugins.workflow.job.WorkflowRun)
_nodes_tree = ('computer[executors[currentExecutable[url]],'
               'oneOffExecutors[currentExecutable[url]]]')

_node_tree = ('executors[currentExecutable[url]],'
              'oneOffExecutors[currentExecutable[url]]')


def _make_node_setting(name, **kwargs):
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
    return {
        'name': name,
        'type': 'hudson.slaves.DumbSlave$DescriptorImpl',
        'json': json.dumps(node_setting)
    }


def _new_builds(jenkins, api_json):
    for computer in api_json['computer']:
        for item in _parse_builds(computer):
            yield new_item(jenkins, 'api4jenkins.build', item)


def _parse_builds(data):
    for kind in ['executors', 'oneOffExecutors']:
        for executor in data.get(kind):
            # in case of issue:
            # https://github.com/joelee2012/api4jenkins/issues/16
            execable = executor['currentExecutable']
            if execable and not execable['_class'].endswith('PlaceholderExecutable'):
                yield {'url': execable['url'], '_class': execable['_class']}


def _iter_node(jenkins, api_json):
    for item in api_json['computer']:
        item['url'] = f"{jenkins.url}computer/{item['displayName']}/"
        yield new_item(jenkins, __name__, item)


def _get_node(jenkins, api_json, name):
    for item in api_json['computer']:
        if name == item['displayName']:
            item['url'] = f"{jenkins.url}computer/{item['displayName']}/"
            return new_item(jenkins, __name__, item)
    return None


class IterBuildingBuildsMixIn:
    # pylint: disable=no-member
    def iter_building_builds(self):
        yield from filter(lambda build: build.building, self.iter_builds())


class Nodes(Item, IterBuildingBuildsMixIn):
    '''
    classdocs
    '''

    def create(self, name, **kwargs):
        self.handle_req('POST', 'doCreateItem',
                        data=_make_node_setting(name, **kwargs))

    def get(self, name):
        return _get_node(self.jenkins, self.api_json(tree='computer[displayName]'), name)

    def iter_builds(self):
        yield from _new_builds(self.jenkins, self.api_json(_nodes_tree, 2))

    def iter(self):
        yield from _iter_node(self.jenkins, self.api_json(tree='computer[displayName]'))

    def filter_node_by_label(self, *labels):
        for node in self:
            for label in node.api_json()['assignedLabels']:
                if label['name'] in labels:
                    yield node

    def filter_node_by_status(self, *, online):
        yield from filter(lambda node: online != node.offline, self)

# following two functions should be used in this module only


class Node(Item, ConfigurationMixIn, DeletionMixIn, RunScriptMixIn, IterBuildingBuildsMixIn):

    def enable(self):
        if self.offline:
            self.handle_req('POST', 'toggleOffline',
                            params={'offlineMessage': ''})

    def disable(self, msg=''):
        if not self.offline:
            self.handle_req('POST', 'toggleOffline',
                            params={'offlineMessage': msg})

    def iter_builds(self):
        for item in _parse_builds(self.api_json(_node_tree, 2)):
            yield new_item(self.jenkins, 'api4jenkins.build', item)

    def __iter__(self):
        yield from self.iter_builds()


class MasterComputerMixIn:
    def __init__(self, jenkins, url):
        # rename built-in node: https://www.jenkins.io/doc/upgrade-guide/2.319/
        name = 'master' if url.endswith('/master/') else 'built-in'
        super().__init__(jenkins, f'{jenkins.url}computer/({name})/')


class MasterComputer(MasterComputerMixIn, Node):
    pass


class SlaveComputer(Node):
    pass


class KubernetesComputer(Node):
    pass


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
    async def create(self, name, **kwargs):
        await self.handle_req('POST', 'doCreateItem', data=_make_node_setting(name, **kwargs))

    async def get(self, name):
        return _get_node(self.jenkins, await self.api_json(tree='computer[displayName]'), name)

    async def iter_builds(self):
        for build in _new_builds(self.jenkins, await self.api_json(_nodes_tree, 2)):
            yield build

    async def aiter(self):
        data = await self.api_json(tree='computer[displayName]')
        for node in _iter_node(self.jenkins, data):
            yield node

    async def filter_node_by_label(self, *labels):
        async for node in self:
            data = await node.api_json()
            for label in data['assignedLabels']:
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
        for item in _parse_builds(await self.api_json(_node_tree, 2)):
            yield new_item(self.jenkins, 'api4jenkins.build', item)

    async def __aiter__(self):
        async for build in self.iter_builds():
            yield build


class AsyncMasterComputer(MasterComputerMixIn, AsyncNode):
    pass


class AsyncSlaveComputer(AsyncNode):
    pass


class AsyncKubernetesComputer(AsyncNode):
    pass


class AsyncDockerComputer(AsyncNode):
    pass


class AsyncEC2Computer(AsyncNode):
    pass
