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

    def test_iter_jobs(self):
        jobs = [job.name for job in self.folder.iter_jobs()]
        self.assertEqual(sorted(jobs), sorted(['pipeline1', 'Level2_Folder1']))

    def test_copy_src_not_found(self):
        with self.assertRaises(BadRequestError):
            self.folder.copy_job('noexist', 'xxxx')

    def test_copy_dest_exists(self):
        with self.assertRaises(BadRequestError):
            self.folder.copy_job('src', 'Level2_Folder1')

    def test_copy(self):
        self.folder2.copy_job('Level2_Folder1', 'Level2_Folder2')
        self.assertIsNotNone(self.folder2.get_job('Level2_Folder2'))

    def test_move(self):
        job = self.folder2.get_job('pipeline1')
        self.assertIsNotNone(job)
        job.move('Level1_Folder2/Level2_Folder1')
        self.assertTrue(job.exists())
        job = self.folder2.get_job('pipeline1')
        self.assertIsNone(job)

    def test_rename(self):
        folder = self.folder3.get_job('Level2_Folder1')
        self.assertTrue(folder.exists())
        folder.rename('Level2_Folder4')
        self.assertTrue(folder.exists())
        folder = self.folder3.get_job('Level2_Folder1')
        self.assertIsNone(folder)

    def test_parent(self):
        folder = self.folder.get_job('Level2_Folder1')
        self.assertEqual(folder.parent, self.folder)
