import time
from pathlib import Path

import pytest
from api4jenkins import Jenkins

from . import setup_jenkins

TEST_DATA_DIR = Path(__file__).with_name('tests_data')


def load_xml(name):
    with open(TEST_DATA_DIR.joinpath(name)) as f:
        return f.read()


@pytest.fixture(scope='module')
def jenkins():
    return Jenkins(setup_jenkins.URL, auth=(setup_jenkins.USER, setup_jenkins.PASSWORD))


@pytest.fixture(scope='module')
def folder_xml():
    return load_xml('folder.xml')


@pytest.fixture(scope='module')
def freejob_xml():
    return load_xml('freestylejob.xml')


@pytest.fixture(scope='module')
def workflow_xml():
    return load_xml('pipeline.xml')


@pytest.fixture(scope='module')
def credential_xml():
    return load_xml('credential.xml')


@pytest.fixture(scope='module')
def view_xml():
    return load_xml('view.xml')

@pytest.fixture
def freejob(jenkins, freejob_xml):
    jenkins.create_job('Level1_FreeJob1', freejob_xml)
    job = jenkins.get_job('Level1_FreeJob1')
    yield job
    job.delete()


@pytest.fixture
def workflow(jenkins, workflow_xml):
    jenkins.create_job('Level1_WorkflowJob1', workflow_xml)
    job = jenkins.get_job('Level1_WorkflowJob1')
    yield job
    job.delete()


@pytest.fixture
def folder(jenkins):
    return jenkins.get_job('Level1_Folder1')


@pytest.fixture(autouse=True)
def setup_folder(jenkins, folder_xml):
    jenkins.create_job('Level1_Folder1', folder_xml)
    jenkins.create_job('Level1_Folder1/Level2_Folder1', folder_xml)
    yield
    jenkins.delete_job('Level1_Folder1')


@pytest.fixture(scope='module')
def retrive_build_and_output():
    def _retrive(item):
        while not item.get_build():
            time.sleep(1)
        build = item.get_build()
        output = []
        for line in build.progressive_output():
            output.append(str(line))
        return build, output
    return _retrive
