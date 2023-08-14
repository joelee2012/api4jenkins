import json
from pathlib import Path

import pytest

from api4jenkins import AsyncJenkins, Jenkins
from api4jenkins.build import FreeStyleBuild, WorkflowRun, AsyncWorkflowRun, AsyncFreeStyleBuild
from api4jenkins.credential import Credential, Credentials, AsyncCredentials, AsyncCredential
from api4jenkins.item import Item, AsyncItem
from api4jenkins.job import Folder, WorkflowJob, WorkflowMultiBranchProject, AsyncFolder, AsyncWorkflowJob, AsyncWorkflowMultiBranchProject
from api4jenkins.node import Node, Nodes, AsyncNode, AsyncNodes
from api4jenkins.plugin import PluginsManager, AsyncPluginsManager
from api4jenkins.queue import Queue, QueueItem, AsyncQueue, AsyncQueueItem
from api4jenkins.report import CoverageReport, CoverageResult, TestReport
from api4jenkins.view import AllView, AsyncAllView

DATA = Path(__file__).with_name('tests_data')


def _api_json(self, tree='', depth=0):
    if self.url == self.jenkins.url:
        return load_json('jenkins/jenkins.json')
    elif isinstance(self, (Folder, AsyncFolder)):
        return load_json('job/folder.json')
    elif isinstance(self, (WorkflowJob, AsyncWorkflowJob)):
        return load_json('job/pipeline.json')
    elif isinstance(self, (WorkflowRun, AsyncWorkflowRun)):
        return load_json('run/workflowrun.json')
    elif isinstance(self, (FreeStyleBuild, AsyncFreeStyleBuild)):
        return load_json('run/freestylebuild.json')
    elif isinstance(self, (Credentials, AsyncCredentials)):
        return load_json('credential/credentials.json')
    elif isinstance(self, (Credential, AsyncCredential)):
        return load_json('credential/user_psw.json')
    elif isinstance(self, (PluginsManager, AsyncPluginsManager)):
        return load_json('plugin/plugin.json')
    elif isinstance(self, (Queue, AsyncQueue)):
        return load_json('queue/queue.json')
    elif isinstance(self, (Nodes, AsyncNodes)):
        return load_json('node/nodes.json')
    elif isinstance(self, (Node, AsyncNode)):
        return load_json('node/node.json')
    elif isinstance(self, AllView):
        return load_json('view/allview.json')
    elif isinstance(self, TestReport):
        return load_json('report/test_report.json')
    elif isinstance(self, CoverageReport):
        return load_json('report/coverage_report.json')
    elif isinstance(self, CoverageResult):
        return load_json('report/coverage_result.json')
    elif isinstance(self, (QueueItem, AsyncQueueItem)):
        return load_json('queue/waitingitem.json')
    raise TypeError(f'unknow item: {type(self)}')


async def _async_api_json(self, tree='', depth=0):
    return _api_json(self, tree, depth)


@pytest.fixture(autouse=True)
def mock_api_json(monkeypatch):
    monkeypatch.setattr(Item, 'api_json', _api_json)
    monkeypatch.setattr(AsyncItem, 'api_json', _async_api_json)


def load_json(file_):
    with open(DATA.joinpath(file_), 'rb') as f:
        return json.load(f)


@pytest.fixture(scope='module')
def url():
    return 'http://0.0.0.0:8080/'


@pytest.fixture(scope='module')
def jenkins(url):
    j = Jenkins(url, auth=('admin', 'password'))
    j._crumb = load_json('jenkins/crumb.json')
    return j


@pytest.fixture(scope='module')
def async_jenkins(url):
    j = AsyncJenkins(url, auth=('admin', 'password'))
    j._crumb = load_json('jenkins/crumb.json')
    return j


@pytest.fixture()
def folder(jenkins):
    return Folder(jenkins, f'{jenkins.url}job/folder/')


@pytest.fixture()
def async_folder(async_jenkins):
    return AsyncFolder(async_jenkins, f'{async_jenkins.url}job/folder/')


@pytest.fixture(scope='module')
def job(jenkins):
    return WorkflowJob(jenkins, f'{jenkins.url}job/folder/job/pipeline/')


@pytest.fixture(scope='module')
def async_job(async_jenkins):
    return AsyncWorkflowJob(async_jenkins, f'{async_jenkins.url}job/folder/job/pipeline/')


@pytest.fixture(scope='module')
def build(jenkins):
    return WorkflowRun(jenkins, f'{jenkins.url}job/folder/job/pipeline/2/')


@pytest.fixture(scope='module')
def async_build(async_jenkins):
    return AsyncWorkflowRun(async_jenkins, f'{async_jenkins.url}job/folder/job/pipeline/2/')


@pytest.fixture(scope='module')
def multi_job(jenkins):
    return WorkflowMultiBranchProject(jenkins, f'{jenkins.url}job/folder/multi-pipe/')


@pytest.fixture(scope='module')
def async_multi_job(async_jenkins):
    return AsyncWorkflowMultiBranchProject(async_jenkins, f'{async_jenkins.url}job/folder/multi-pipe/')


@pytest.fixture(scope='module')
def credential(jenkins):
    return Credential(jenkins, f'{jenkins.url}credentials/store/system/domain/_/test-user/')


@pytest.fixture(scope='module')
def async_credential(async_jenkins):
    return AsyncCredential(async_jenkins, f'{async_jenkins.url}credentials/store/system/domain/_/test-user/')


@pytest.fixture(scope='module')
def view(jenkins):
    return AllView(jenkins, jenkins.url)


@pytest.fixture(scope='module')
def async_view(async_jenkins):
    return AsyncAllView(async_jenkins, async_jenkins.url)

# @pytest.fixture
# def mock_resp():
#     with respx.mock() as respx_mock:
#         yield respx_mock


@pytest.fixture
def test_report(jenkins, build):
    return TestReport(jenkins, f'{build.url}testReport')

# @pytest.fixture
# def coverage_report(jenkins, workflow):
#     return workflow.get
