import json
from pathlib import Path

import pytest

from api4jenkins import Jenkins
from api4jenkins.build import FreeStyleBuild, WorkflowRun
from api4jenkins.credential import Credential, Credentials
from api4jenkins.item import Item
from api4jenkins.job import Folder, WorkflowJob, WorkflowMultiBranchProject
from api4jenkins.node import Node, Nodes
from api4jenkins.plugin import PluginsManager
from api4jenkins.queue import Queue, QueueItem
from api4jenkins.report import CoverageReport, CoverageResult, TestReport
from api4jenkins.view import AllView

DATA = Path(__file__).with_name('tests_data')


def _api_json(self, tree='', depth=0):
    if self.url == self.jenkins.url:
        return load_json('jenkins/jenkins.json')
    elif isinstance(self, Folder):
        return load_json('job/folder.json')
    elif isinstance(self, WorkflowJob):
        return load_json('job/pipeline.json')
    elif isinstance(self, WorkflowRun):
        return load_json('run/workflowrun.json')
    elif isinstance(self, FreeStyleBuild):
        return load_json('run/freestylebuild.json')
    elif isinstance(self, Credentials):
        return load_json('credential/credentials.json')
    elif isinstance(self, Credential):
        return load_json('credential/user_psw.json')
    elif isinstance(self, PluginsManager):
        return load_json('plugin/plugin.json')
    elif isinstance(self, Queue):
        return load_json('queue/queue.json')
    elif isinstance(self, Nodes):
        return load_json('node/nodes.json')
    elif isinstance(self, Node):
        return load_json('node/node.json')
    elif isinstance(self, AllView):
        return load_json('view/allview.json')
    elif isinstance(self, TestReport):
        return load_json('report/test_report.json')
    elif isinstance(self, CoverageReport):
        return load_json('report/coverage_report.json')
    elif isinstance(self, CoverageResult):
        return load_json('report/coverage_result.json')
    elif isinstance(self, QueueItem):
        return load_json('queue/waitingitem.json')
    raise TypeError(f'unknow item: {type(self)}')


@pytest.fixture(autouse=True)
def mock_api_json(monkeypatch):
    monkeypatch.setattr(Item, 'api_json', _api_json)


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


@pytest.fixture()
def folder(jenkins):
    return Folder(jenkins, f'{jenkins.url}job/Level1_Folder1/')


@pytest.fixture(scope='module')
def pipeline(jenkins):
    return WorkflowJob(jenkins, f'{jenkins.url}job/Level1_WorkflowJob1/')


@pytest.fixture(scope='module')
def workflowrun(jenkins):
    return WorkflowRun(jenkins, f'{jenkins.url}job/Level1_WorkflowJob1/2/')


@pytest.fixture(scope='module')
def multibranchproject(jenkins):
    return WorkflowMultiBranchProject(jenkins, f'{jenkins.url}job/Level1_WorkflowMultiBranchProject/')


@pytest.fixture(scope='module')
def new_credential(jenkins):
    return Credential(jenkins, f'{jenkins.url}credentials/store/system/domain/_/test-user/')


@pytest.fixture(scope='module')
def view(jenkins):
    return AllView(jenkins, jenkins.url)


# @pytest.fixture
# def mock_resp():
#     with respx.mock() as respx_mock:
#         yield respx_mock


@pytest.fixture
def test_report(jenkins, workflowrun):
    return TestReport(jenkins, f'{workflowrun.url}testReport')

# @pytest.fixture
# def coverage_report(jenkins, workflow):
#     return workflow.get
