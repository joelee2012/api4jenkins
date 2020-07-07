# encoding: utf-8

from pathlib import Path
import unittest

from jenkinsx import Jenkins
from jenkinsx.build import WorkflowRun
from jenkinsx.exceptions import BadRequestError
from jenkinsx.item import snake
from jenkinsx.job import Folder, WorkflowJob

TEST_DATA_DIR = Path(__file__).with_name('tests_data')


def load_test_xml(name):
    with open(TEST_DATA_DIR.joinpath(name)) as f:
        return f.read()


class TestFolder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from . import setup_jenkins
        j = Jenkins(setup_jenkins.URL, auth=(
            setup_jenkins.USER, setup_jenkins.PASSWORD))
        xml = load_test_xml('folder.xml')
        j.create_job('Level1_Folder1', xml)
        j.create_job('Level1_Folder2', xml)
        j.create_job('Level1_Folder3', xml)
        j.create_job('Level1_Folder1/Level2_Folder1', xml)
        j.create_job('Level1_Folder2/Level2_Folder1', xml)
        j.create_job('Level1_Folder3/Level2_Folder1', xml)
        xml = load_test_xml('pipeline.xml')
        j.create_job('Level1_Folder1/pipeline1', xml)
        j.create_job('Level1_Folder2/pipeline1', xml)
        cls.folder = j.get_job('Level1_Folder1')
        cls.folder2 = j.get_job('Level1_Folder2')
        cls.folder3 = j.get_job('Level1_Folder3')

    @classmethod
    def tearDownClass(cls):
        cls.folder.delete()
        cls.folder2.delete()
        cls.folder3.delete()

    def test_iter_should_iter_folder_with_depth(self):
        jobs = [job.name for job in self.folder.iter()]
        self.assertEqual(sorted(jobs), sorted(['pipeline1', 'Level2_Folder1']))

    def test_copy_should_raise_exception_if_src_not_found(self):
        with self.assertRaises(BadRequestError):
            self.folder.copy('noexist', 'xxxx')

    def test_copy_should_raise_exception_if_dest_exists(self):
        with self.assertRaises(BadRequestError):
            self.folder.copy('src', 'Level2_Folder1')

    def test_copy_should_create_new_job_from_src_job(self):
        self.folder2.copy('Level2_Folder1', 'Level2_Folder2')
        self.assertIsNotNone(self.folder2.get('Level2_Folder2'))

    def test_move_should_move_job_to_give_path(self):
        job = self.folder2.get('pipeline1')
        self.assertIsNotNone(job)
        job.move('Level1_Folder2/Level2_Folder1')
        self.assertTrue(job.exists())
        job = self.folder2.get('pipeline1')
        self.assertIsNone(job)

    def test_rename_should_rename_job_with_given_name(self):
        folder = self.folder3.get('Level2_Folder1')
        self.assertTrue(folder.exists())
        folder.rename('Level2_Folder4')
        self.assertTrue(folder.exists())
        folder = self.folder3.get('Level2_Folder1')
        self.assertIsNone(folder)

    def test_parent_should_get_correct_parent(self):
        folder = self.folder.get('Level2_Folder1')
        self.assertEqual(folder.parent, self.folder)
