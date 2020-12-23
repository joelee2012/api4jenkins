# encoding: utf-8

from pathlib import Path
import logging
import time
import unittest

from api4jenkins import Jenkins
from api4jenkins.exceptions import ItemNotFoundError, AuthenticationError, \
    BadRequestError
from api4jenkins.item import snake
from api4jenkins.job import Folder


logging.basicConfig(level=logging.DEBUG)

TEST_DATA_DIR = Path(__file__).with_name('tests_data')


def load_test_xml(name):
    with open(TEST_DATA_DIR.joinpath(name)) as f:
        return f.read()


class TestJenkins(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from . import setup_jenkins
        cls.jx = Jenkins(setup_jenkins.URL, auth=(
            setup_jenkins.USER, setup_jenkins.PASSWORD))
        cls.folder_xml = load_test_xml('folder.xml')

    def tearDown(self):
        self.jx.delete_job('Level1_Folder1')

    def test_should_raise_exception_if_init_with_invalid_auth(self):
        jx = Jenkins(self.jx.url, auth=('admin', 'admin'))
        with self.assertRaises(AuthenticationError):
            jx.api_json()

    @unittest.skip
    def test_jenkins_should_has_dynamic_attributes(self):
        dynamic_attrs = {snake(k): v for k, v in self.jx.api_json().items()
                         if isinstance(v, (int, str, bool, type(None)))}
        self.assertEqual(sorted(self.jx.attrs),
                         sorted(dynamic_attrs.keys()))
        for key, value in dynamic_attrs.items():
            with self.subTest(value=value):
                self.assertEqual(getattr(self.jx, key), value)

    def test_get_job_should_return_none_if_job_not_exists(self):
        folder = self.jx.get_job('Level1_Folder1')
        self.assertIsNone(folder)

    def test_get_job_should_return_job_if_job_exists(self):
        self.jx.create_job('Level1_Folder1', self.folder_xml)
        folder = self.jx.get_job('Level1_Folder1')
        self.assertIsInstance(folder, Folder)
        self.assertEqual(str(folder),
                         f'<Folder: {self.jx.url}job/Level1_Folder1/>')
        folder2 = self.jx.get_job('Level1_Folder1/Level2_Folder1')
        self.assertIsNone(folder2)
        self.jx.create_job('Level1_Folder1/Level2_Folder1', self.folder_xml)
        folder2 = self.jx.get_job('Level1_Folder1/Level2_Folder1')
        self.assertIsInstance(folder2, Folder)
        self.assertEqual(str(folder2),
                         f'<Folder: {self.jx.url}job/Level1_Folder1/'
                         'job/Level2_Folder1/>')
#

    def test_create_job_should_raise_exception_if_job_exists(self):
        self.jx.create_job('Level1_Folder1', self.folder_xml)
        with self.assertRaises(BadRequestError):
            self.jx.create_job('Level1_Folder1', self.folder_xml)

    def test_create_job_should_raise_exception_if_name_illegal(self):
        with self.assertRaisesRegex(BadRequestError,
                                    '@  is an unsafe character'):
            self.jx.create_job('Level2@new', '')

    def test_build_job_should_raise_exception_if_job_not_found(self):
        with self.assertRaisesRegex(ItemNotFoundError,
                                    'No such job: '
                                    'Level1_Folder1'):
            self.jx.build_job('Level1_Folder1')

    def test_build_job_should_raise_exception_if_job_unbuildable(self):
        self.jx.create_job('Level1_Folder1', self.folder_xml)
        with self.assertRaisesRegex(AttributeError,
                                    "'Folder' object has no attribute 'build'"):
            self.jx.build_job('Level1_Folder1')

    def test_build_job_should_run_without_parameters(self):
        xml = load_test_xml('pipeline.xml')
        self.jx.create_job('pipeline', xml)
        job = self.jx.get_job('pipeline')
        item = job.build()
        self.assertEqual(item.get_job(), job)
        while not item.get_build():
            time.sleep(1)
        build = item.get_build()
        self.assertEqual(build.get_job(), job)
        output = []
        for line in build.progressive_output():
            output.append(str(line))
        self.assertIn(self.jx.version, ''.join(output))
        output = []
        for line in build.console_text():
            output.append(str(line))
        self.assertIn(self.jx.version, ''.join(output))
        while build.building:
            time.sleep(1)
        self.assertEqual(build, job.get_last_build())

    def test_exists_should_return_true_if_jenkins_exists(self):
        from . import setup_jenkins
        jx = Jenkins(setup_jenkins.URL, auth=(
            setup_jenkins.USER, setup_jenkins.PASSWORD))
        self.assertTrue(jx.exists())
        jx = Jenkins(setup_jenkins.URL)
        self.assertTrue(jx.exists())

    def test_exists_should_return_false_if_jenkins_not_exists(self):
        jx = Jenkins('http://localhost:8080')
        self.assertFalse(jx.exists())

    def test_jenkins_should_create_credential_if_not_exists(self):
        cred = self.jx.credentials.get('user-id')
        self.assertIsNone(cred)
        self.jx.credentials.create(load_test_xml('credential.xml'))
        cred = self.jx.credentials.get('user-id')
        self.assertEqual(cred.id, 'user-id')
