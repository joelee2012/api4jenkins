# encoding: utf-8

import json
from typing import Any, Dict, Iterator, AsyncIterator, Optional, List
from httpx import Response
from .build import Build, AsyncBuild

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


from abc import abstractmethod

class IterBuildingBuildsMixIn:
    @abstractmethod
    def iter_builds(self) -> Iterator[Build]: ...
    
    # pylint: disable=no-member
    def iter_building_builds(self) -> Iterator[Build]:
        yield from filter(lambda build: build.building, self.iter_builds())


class Nodes(Item, IterBuildingBuildsMixIn):
    '''
    classdocs
    '''

    def create(self, name: str, **kwargs: Any) -> Response:
        return self.handle_req('POST', 'doCreateItem',
                             data=_make_node_setting(name, **kwargs))

    def get(self, name: str) -> Optional['Node']:
        return _get_node(self.jenkins, self.api_json(tree='computer[displayName]'), name)

    def iter_builds(self) -> Iterator[Build]:
        yield from _new_builds(self.jenkins, self.api_json(_nodes_tree, 2))

    def iter(self) -> Iterator['Node']:
        yield from _iter_node(self.jenkins, self.api_json(tree='computer[displayName]'))

    def filter_node_by_label(self, *labels: str) -> Iterator['Node']:
        for node in self:
            for label in node.api_json()['assignedLabels']:
                if label['name'] in labels:
                    yield node

    def filter_node_by_status(self, *, online: bool) -> Iterator['Node']:
        yield from filter(lambda node: online != node.offline, self)

# following two functions should be used in this module only


class Node(Item, ConfigurationMixIn, DeletionMixIn, RunScriptMixIn, IterBuildingBuildsMixIn):

    def enable(self) -> Optional[Response]:
        if self.offline:
            return self.handle_req('POST', 'toggleOffline',
                                 params={'offlineMessage': ''})
        return None

    def disable(self, msg: str = '') -> Optional[Response]:
        if not self.offline:
            return self.handle_req('POST', 'toggleOffline',
                                 params={'offlineMessage': msg})
        return None

    def iter_builds(self) -> Iterator[Build]:  # type: ignore[override]
        """Override Item.iter_builds() to provide build iteration.
        Note: This intentionally changes the return type."""
        for item in _parse_builds(self.api_json(_node_tree, 2)):
            yield new_item(self.jenkins, 'api4jenkins.build', item)

    def __iter__(self) -> Iterator[Build]:  # type: ignore[override]
        """Override Item.__iter__() to provide build iteration.
        Note: This intentionally changes the return type."""
        yield from self.iter_builds()


class MasterComputerMixIn:
    def __init__(self, jenkins: Any, url: str) -> None:
        """Initialize master computer with proper URL.
        Args:
            jenkins: Jenkins instance
            url: Base URL for the computer
        """
        # rename built-in node: https://www.jenkins.io/doc/upgrade-guide/2.319/
        name = 'master' if url.endswith('/master/') else 'built-in'
        super().__init__(jenkins, f'{jenkins.url}computer/({name})/')  # type: ignore


class MasterComputer(MasterComputerMixIn, Node):
    pass  # Inherits all type annotations from Node and MasterComputerMixIn


class SlaveComputer(Node):
    pass  # Inherits all type annotations from Node


class KubernetesComputer(Node):
    pass  # Inherits all type annotations from Node


class DockerComputer(Node):
    pass  # Inherits all type annotations from Node


class EC2Computer(Node):
    pass  # Inherits all type annotations from Node


class AsyncIterBuildingBuildsMixIn:
    @abstractmethod
    async def iter_builds(self) -> AsyncIterator[AsyncBuild]: ...
    
    # pylint: disable=no-member
    async def iter_building_builds(self) -> AsyncIterator[AsyncBuild]:
        async for build in self.iter_builds():
            if await build.building:
                yield build


class AsyncNodes(AsyncItem, AsyncIterBuildingBuildsMixIn):
    async def create(self, name: str, **kwargs: Any) -> Response:
        return await self.handle_req('POST', 'doCreateItem', 
                                   data=_make_node_setting(name, **kwargs))

    async def get(self, name: str) -> Optional['AsyncNode']:
        return _get_node(self.jenkins, await self.api_json(tree='computer[displayName]'), name)

    async def iter_builds(self) -> AsyncIterator[AsyncBuild]:  # type: ignore[override]
        """Override AsyncItem.iter_builds() to provide async build iteration.
        Note: This intentionally changes the return type."""
        for build in _new_builds(self.jenkins, await self.api_json(_nodes_tree, 2)):
            yield build

    async def aiter(self) -> AsyncIterator['AsyncNode']:  # type: ignore[override]
        """Override AsyncItem.aiter() to provide async node iteration.
        Note: This intentionally changes the return type."""
        data = await self.api_json(tree='computer[displayName]')
        for node in _iter_node(self.jenkins, data):
            yield node

    async def filter_node_by_label(self, *labels: str) -> AsyncIterator['AsyncNode']:
        async for node in self:
            data = await node.api_json()
            for label in data['assignedLabels']:
                if label['name'] in labels:
                    yield node

    async def filter_node_by_status(self, *, online: bool) -> AsyncIterator['AsyncNode']:
        async for node in self:
            if online != await node.offline:
                yield node


class AsyncNode(AsyncItem, AsyncConfigurationMixIn, AsyncDeletionMixIn, AsyncRunScriptMixIn, AsyncIterBuildingBuildsMixIn):

    async def enable(self) -> Optional[Response]:
        if await self.offline:
            return await self.handle_req('POST', 'toggleOffline',
                                       params={'offlineMessage': ''})
        return None

    async def disable(self, msg: str = '') -> Optional[Response]:
        if not await self.offline:
            return await self.handle_req('POST', 'toggleOffline',
                                       params={'offlineMessage': msg})
        return None

    async def iter_builds(self) -> AsyncIterator[AsyncBuild]:  # type: ignore[override]
        """Override AsyncItem.iter_builds() to provide async build iteration.
        Note: This intentionally changes the return type."""
        for item in _parse_builds(await self.api_json(_node_tree, 2)):
            yield new_item(self.jenkins, 'api4jenkins.build', item)

    async def __aiter__(self) -> AsyncIterator[AsyncBuild]:  # type: ignore[override]
        """Override AsyncItem.__aiter__() to provide async build iteration.
        Note: This intentionally changes the return type."""
        async for build in self.iter_builds():
            yield build


class AsyncMasterComputer(MasterComputerMixIn, AsyncNode):
    pass  # Inherits all type annotations from AsyncNode and MasterComputerMixIn


class AsyncSlaveComputer(AsyncNode):
    pass  # Inherits all type annotations from AsyncNode


class AsyncKubernetesComputer(AsyncNode):
    pass  # Inherits all type annotations from AsyncNode


class AsyncDockerComputer(AsyncNode):
    pass  # Inherits all type annotations from AsyncNode


class AsyncEC2Computer(AsyncNode):
    pass  # Inherits all type annotations from AsyncNode
