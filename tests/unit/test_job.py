# encoding: utf-8

import unittest

import responses

from api4jenkins import Jenkins
from api4jenkins.build import WorkflowRun
from api4jenkins.exceptions import BadRequestError
from api4jenkins.item import snake
from api4jenkins.job import Folder, WorkflowJob
from .help import mock_get, load_test_json, responses_count,\
    mock_post, JENKINS_URL


class TestFolder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.folder_json = load_test_json('job/folder.json')
        cls.crumb = load_test_json('jenkins/crumb.json')

    def setUp(self):
        mock_get(f'{JENKINS_URL}crumbIssuer/api/json',
                 json=self.crumb)
        mock_get(f'{JENKINS_URL}job/Level1_Folder1/api/json',
                 json=self.folder_json)
        self.jx = Jenkins(JENKINS_URL, auth=('admin', 'admin'))
        self.folder = Folder(
            self.jx, f'{JENKINS_URL}job/Level1_Folder1/')

    @responses.activate
    def test_create_job_when_exists(self):
        mock_post(
            f'{JENKINS_URL}job/Level1_Folder1/createItem',
            headers={
                'X-Error': "A job already exists with"
                " the name 'Level2_Folder1'"},
            status=400)
        with self.assertRaises(BadRequestError):
            self.folder.create('Level2_Folder1', '')
        self.assertEqual(responses_count(), 2)

    @responses.activate
    def test_create_job_when_name_illegal(self):
        mock_post(
            f'{JENKINS_URL}job/Level1_Folder1/createItem',
            headers={'X-Error': '@  is an unsafe character'},
            status=400)
        with self.assertRaisesRegex(BadRequestError,
                                    '@  is an unsafe character'):
            self.folder.create('Level2@new', '')
        self.assertEqual(responses_count(), 2)

    @responses.activate
    def test_create_job(self):
        mock_post(
            f'{JENKINS_URL}job/Level1_Folder1/createItem?name=Levevl2_new',
            match_querystring=True)
        self.folder.create('Levevl2_new', '')
        self.assertEqual(responses_count(), 2)

    @responses.activate
    def test_get_job_when_not_found(self):
        not_found = self.folder.get('notfound')
        self.assertIsNone(not_found)
        self.assertEqual(responses_count(), 2)

    @responses.activate
    def test_get_job(self):
        self.assertIsInstance(self.folder, Folder)
        self.assertEqual(str(self.folder),
                         '<Folder: http://0.0.0.0:8080/job/Level1_Folder1/>')
        level2_folder1 = self.folder.get('Level2_Folder1')
        self.assertIsInstance(level2_folder1, Folder)
        self.assertEqual(str(level2_folder1),
                         '<Folder: http://0.0.0.0:8080/job/Level1_Folder1/'
                         'job/Level2_Folder1/>')
        self.assertEqual(responses_count(), 2)

    @responses.activate
    def test_iter_jobs(self):
        jobs = list(self.folder.iter())
        self.assertEqual(len(jobs), 4)
        self.assertEqual(responses_count(), 2)

    @responses.activate
    def test_copy_src_not_found(self):
        mock_post(
            f'{JENKINS_URL}job/Level1_Folder1/createItem',
            headers={
                'X-Error': 'No such job: xxxx'},
            status=400)
        with self.assertRaises(BadRequestError):
            self.folder.copy('noexist', 'xxxx')

    @responses.activate
    def test_copy_dest_exists(self):
        mock_post(
            f'{JENKINS_URL}job/Level1_Folder1/createItem',
            headers={
                'X-Error': "A job already exists with"
                " the name 'Level2_Folder1'"},
            status=400)
        with self.assertRaises(BadRequestError):
            self.folder.copy('src', 'Level2_Folder1')

    @responses.activate
    def test_copy(self):
        mock_post(
            f'{JENKINS_URL}job/Level1_Folder1/createItem')
        self.folder.copy('Level2_Folder1', 'Level2_Folder2')
        self.assertEqual(responses_count(), 2)

    @responses.activate
    def test_move(self):
        headers = {'Location': f'{JENKINS_URL}job/Level1_Folder2/'
                   'job/Level2_Folder1/job/Level1_Folder1'}
        mock_post(f'{JENKINS_URL}job/Level1_Folder1/move/move',
                  headers=headers)
        self.folder.move('Level1_Folder2/Level2_Folder1')
        self.assertEqual(self.folder.url, headers['Location'])
        self.assertEqual(responses_count(), 2)

    @responses.activate
    def test_rename(self):
        headers = {'Location': f'{JENKINS_URL}job/Level1_Folder2/'}
        mock_post(f'{JENKINS_URL}job/Level1_Folder1/confirmRename',
                  headers=headers)
        self.folder.rename('Level1_Folder2')
        self.assertEqual(self.folder.url, headers['Location'])
        self.assertEqual(responses_count(), 2)

    @responses.activate
    def test_parent(self):
        self.assertEqual(self.folder.parent, self.jx)
        self.assertIsInstance(self.folder.parent, Jenkins)
        folder = Folder(self.jx, f'{JENKINS_URL}job/Level1_Folder1/'
                        'job/Level2_Folder1/')
        folder.full_name = 'Level1_Folder1/Level2_Folder1/'
        self.assertEqual(folder.parent, self.folder)
        self.assertIsInstance(folder.parent, Folder)
        self.assertEqual(folder.parent.parent, self.jx)

    @responses.activate
    def test_dynamic_attributes(self):
        dynamic_attrs = {snake(k): v for k, v in
                         self.folder_json.items()
                         if isinstance(v, (int, str, bool, type(None)))}
        self.assertEqual(sorted(self.folder.attrs),
                         sorted(dynamic_attrs.keys()))
        for key, value in dynamic_attrs.items():
            with self.subTest(value=value):
                self.assertEqual(getattr(self.folder, key), value)


class TestProject(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.workflow_json = load_test_json('job/pipeline.json')
        cls.crumb = load_test_json('jenkins/crumb.json')

    def setUp(self):
        mock_get(f'{JENKINS_URL}crumbIssuer/api/json',
                 json=self.crumb)
        mock_get(f'{JENKINS_URL}job/Level1_WorkflowJob/api/json',
                 json=self.workflow_json)
        self.jx = Jenkins(JENKINS_URL, auth=('admin', 'admin'))
        self.project = WorkflowJob(
            self.jx, f'{JENKINS_URL}job/Level1_WorkflowJob/')

    @responses.activate
    def test_build_without_parameters(self):
        mock_post(f'{JENKINS_URL}job/Level1_WorkflowJob/build',
                  headers={'Location':
                           f'{JENKINS_URL}queue/item/53/'})
        item = self.project.build()
        self.assertEqual(item.url, f'{JENKINS_URL}queue/item/53/')

    @responses.activate
    def test_build_with_parameters(self):
        mock_post(f'{JENKINS_URL}job/Level1_WorkflowJob/buildWithParameters',
                  headers={'Location':
                           f'{JENKINS_URL}queue/item/53/'})
        item = self.project.build(parameter='xxx')
        self.assertEqual(item.url, f'{JENKINS_URL}queue/item/53/')

    @responses.activate
    def test_get_build(self):
        build = self.project.get_build(52)
        self.assertIsInstance(build, WorkflowRun)
        self.assertEqual(
            build.url, f'{JENKINS_URL}job/Level1_WorkflowJob/52/')
        build = self.project.get_build(55)
        self.assertIsNone(build)

    @responses.activate
    def test_get_builds(self):
        builds = list(self.project.iter_builds())
        self.assertEqual(len(builds), 8)

    @responses.activate
    def test_get_special_build(self):
        for key in ['firstBuild', 'lastBuild', 'lastCompletedBuild',
                    'lastFailedBuild', 'lastStableBuild', 'lastUnstableBuild',
                    'lastSuccessfulBuild', 'lastUnsuccessfulBuild']:
            func = getattr(self.project, snake(f'get_{key}'))
            with self.subTest(key=key):
                build = func()
                if key == 'lastUnstableBuild':
                    self.assertIsNone(build)
                    continue
                self.assertIsInstance(build, WorkflowRun)
                self.assertEqual(build.url, self.workflow_json[key]['url'])

    @responses.activate
    def test_dynamic_attributes(self):
        dynamic_attrs = {snake(k): v for k, v in
                         self.workflow_json.items()
                         if isinstance(v, (int, str, bool, type(None)))}
        self.assertEqual(sorted(self.project.attrs),
                         sorted(dynamic_attrs.keys()))
        for key, value in dynamic_attrs.items():
            with self.subTest(value=value):
                self.assertEqual(getattr(self.project, key), value)
        self.assertEqual(responses_count(), len(dynamic_attrs.keys())+1)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
