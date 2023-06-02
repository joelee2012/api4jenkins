import asyncio
import contextlib
import os
import sys
import time
from pathlib import Path

import pytest
from api4jenkins import Jenkins, WorkflowJob, Folder, EMPTY_FOLDER_XML, AsyncJenkins, AsyncFolder, AsyncWorkflowJob

TEST_DATA_DIR = Path(__file__).with_name('tests_data')


def load_xml(name):
    with open(TEST_DATA_DIR.joinpath(name)) as f:
        return f.read()


@pytest.fixture(scope='session')
def jenkins():
    yield Jenkins(os.environ['JENKINS_URL'], auth=(
        os.environ['JENKINS_USER'], os.environ['JENKINS_PASSWORD']))


@pytest.fixture(scope='session')
def async_jenkins():
    yield AsyncJenkins(os.environ['JENKINS_URL'], auth=(
        os.environ['JENKINS_USER'], os.environ['JENKINS_PASSWORD']))


@pytest.fixture(scope='session')
def folder_xml():
    return EMPTY_FOLDER_XML


# @pytest.fixture(scope='session')
# def job_xml():
#     return load_xml('job.xml')


# @pytest.fixture(scope='session')
# def job_with_args_xml():
#     return load_xml('job_params.xml')


@pytest.fixture(scope='session')
def credential_xml():
    return load_xml('credential.xml')


@pytest.fixture(scope='session')
def view_xml():
    return load_xml('view.xml')


@pytest.fixture(scope='session')
def folder(jenkins: Jenkins):
    return Folder(jenkins, jenkins._name2url('folder'))


@pytest.fixture(scope='session')
def async_folder(async_jenkins: AsyncJenkins):
    return AsyncFolder(async_jenkins, async_jenkins._name2url('async_folder'))


@pytest.fixture(scope='session')
def job(jenkins: Jenkins):
    return WorkflowJob(jenkins, jenkins._name2url('folder/job'))


@pytest.fixture(scope='session')
def async_job(async_jenkins: AsyncJenkins):
    return AsyncWorkflowJob(async_jenkins, async_jenkins._name2url('async_folder/job'))


@pytest.fixture(scope='session')
def args_job(jenkins: Jenkins):
    return WorkflowJob(jenkins, jenkins._name2url('folder/args_job'))


@pytest.fixture(scope='session')
def async_args_job(async_jenkins: AsyncJenkins):
    return AsyncWorkflowJob(async_jenkins, async_jenkins._name2url('async_folder/args_job'))


@pytest.fixture(scope='session', autouse=True)
def setup(jenkins, credential_xml, view_xml):
    for name in ['folder/folder', 'folder/for_rename', 'folder/for_move', 'async_folder/folder', 'async_folder/for_rename', 'async_folder/for_move']:
        jenkins.create_job(name, EMPTY_FOLDER_XML, True)

    for name in ['folder/job', 'async_folder/job']:
        jenkins.create_job(name, load_xml('job.xml'))

    for name in ['folder/args_job', 'async_folder/args_job']:
        jenkins.create_job(name, load_xml('args_job.xml'))

    jenkins.credentials.create(credential_xml)
    jenkins.views.create('global-view', view_xml)
    jenkins['folder'].credentials.create(credential_xml)
    jenkins['folder'].views.create('folder-view', view_xml)

    yield
    jenkins.delete_job('folder')
    jenkins.delete_job('async_folder')
    jenkins.credentials.get('user-id').delete()
    jenkins.views.get('global-view').delete()


@pytest.fixture(scope='session')
def retrive_build_and_output():
    def _retrive(item):
        for _ in range(10):
            if item.get_build():
                break
            time.sleep(1)
        else:
            raise TimeoutError('unable to get build in 10 seconds!!')
        build = item.get_build()
        output = []
        for line in build.progressive_output():
            output.append(str(line))
        return build, output
    return _retrive


# workaround for https://github.com/pytest-dev/pytest-asyncio/issues/371
@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    if loop.is_running():
        asyncio.sleep(2)
    loop.close()
