# encoding: utf-8

import json
import re

from .exceptions import ItemNotFoundError
from .item import Item
from .mix import ConfigurationMixIn, DeletionMixIn, RunScriptMixIn


class Nodes(Item):
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
        tree = 'computer[oneOffExecutors[currentExecutable[url]]]'
        for computer in self.api_json(tree, 2)['computer']:
            for executor in computer.get('oneOffExecutors'):
                # in case of issue:
                # https://github.com/joelee2012/api4jenkins/issues/16
                if not executor['currentExecutable']:
                    continue
                yield self._new_instance_by_item('api4jenkins.build',
                                                 executor['currentExecutable'])

    def __iter__(self):
        for item in self.api_json(tree='computer[displayName]')['computer']:
            item['url'] = f"{self.url}{item['displayName']}/"
            yield self._new_instance_by_item(__name__, item)


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
        tree = 'oneOffExecutors[currentExecutable[url]]'
        for executor in self.api_json(tree, 2)['oneOffExecutors']:
            yield self._new_instance_by_item('api4jenkins.build',
                                             executor['currentExecutable'])


class MasterComputer(Node):
    def __init__(self, jenkins, url):
        super().__init__(jenkins, re.sub(r'/master/$', '/(master)/', url))


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
