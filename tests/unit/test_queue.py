# encoding: utf-8
import unittest

import responses

from api4jenkins import Jenkins
from api4jenkins.build import WorkflowRun
from api4jenkins.job import WorkflowJob
from api4jenkins.queue import QueueItem
from .help import load_test_json, mock_get, JENKINS_URL


class TestQueue(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.queue_json = load_test_json('queue/queue.json')
        cls.crumb = load_test_json('jenkins/crumb.json')

    def setUp(self):
        mock_get(f'{JENKINS_URL}crumbIssuer/api/json',
                 json=self.crumb)
        mock_get(f'{JENKINS_URL}queue/api/json',
                 json=self.queue_json)
        self.jx = Jenkins(JENKINS_URL, auth=('admin', 'admin'))

    @responses.activate
    def test_get_none_if_id_not_exist(self):
        self.assertIsNone(self.jx.queue.get(1))

    @responses.activate
    def test_get_item_if_id_exist(self):
        self.assertIsInstance(self.jx.queue.get(669), QueueItem)

    @responses.activate
    def test_get_all_items(self):
        for item in self.jx.queue:
            with self.subTest(url=item.url):
                self.assertIsInstance(item, QueueItem)


class TestQueueItem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.crumb = load_test_json('jenkins/crumb.json')

    def setUp(self):
        mock_get(f'{JENKINS_URL}crumbIssuer/api/json',
                 json=self.crumb)
        self.jx = Jenkins(JENKINS_URL, auth=('admin', 'admin'))

    @responses.activate
    def test_get_job_for_blocked_item(self):
        item = QueueItem(self.jx, f'{JENKINS_URL}queue/item/669/')
        mock_get(f'{JENKINS_URL}queue/item/669/api/json',
                 json=load_test_json('queue/blockeditem.json'))
        job = item.get_job()
        self.assertIsInstance(job, WorkflowJob)
        self.assertEqual(
            job.url, f'{JENKINS_URL}job/Level1_WorkflowJob1/')

    @responses.activate
    def test_get_job_for_left_Item(self):
        item = QueueItem(self.jx, f'{JENKINS_URL}queue/item/599/')
        mock_get(f'{JENKINS_URL}queue/item/599/api/json',
                 json=load_test_json('queue/leftitem.json'))
        job = item.get_job()
        self.assertIsInstance(job, WorkflowJob)
        self.assertEqual(
            job.url, f'{JENKINS_URL}job/Level1_WorkflowJob1/')

    @responses.activate
    def test_get_job_for_waiting_Item(self):
        item = QueueItem(self.jx, f'{JENKINS_URL}queue/item/700/')
        mock_get(f'{JENKINS_URL}queue/item/700/api/json',
                 json=load_test_json('queue/waitingitem.json'))
        job = item.get_job()
        self.assertIsInstance(job, WorkflowJob)
        self.assertEqual(
            job.url, f'{JENKINS_URL}job/Level1_WorkflowJob1/')

    @responses.activate
    def test_get_job_for_buildable_item(self):
        item = QueueItem(self.jx, f'{JENKINS_URL}queue/item/668/')
        mock_get(f'{JENKINS_URL}queue/item/668/api/json',
                 json=load_test_json('queue/buildableitem.json'))
        mock_get(f'{JENKINS_URL}computer/api/json',
                 json=load_test_json('node/computer.json'))
        mock_get(f'{JENKINS_URL}job/Level1_WorkflowJob1/54/api/json',
                 json={'queueId': 667})
        mock_get(f'{JENKINS_URL}api/json',
                 json=load_test_json('jenkins/jenkins.json'))
        job = item.get_job()
        self.assertIsInstance(job, WorkflowJob)
        self.assertEqual(
            job.url, f'{JENKINS_URL}job/Level1_WorkflowJob1/')

    @responses.activate
    def test_get_build_for_blocked_item(self):
        item = QueueItem(self.jx, f'{JENKINS_URL}queue/item/669/')
        mock_get(f'{JENKINS_URL}queue/item/669/api/json',
                 json=load_test_json('queue/blockeditem.json'))
        job = item.get_build()
        self.assertIsNone(job)

    @responses.activate
    def test_get_build_for_left_item(self):
        item = QueueItem(self.jx, f'{JENKINS_URL}queue/item/599/')
        mock_get(f'{JENKINS_URL}queue/item/599/api/json',
                 json=load_test_json('queue/leftitem.json'))
        build = item.get_build()
        self.assertIsInstance(build, WorkflowRun)
        self.assertEqual(
            build.url, f'{JENKINS_URL}job/Level1_WorkflowJob1/54/')

    @responses.activate
    def test_get_build_for_waiting_item(self):
        item = QueueItem(self.jx, f'{JENKINS_URL}queue/item/700/')
        mock_get(f'{JENKINS_URL}queue/item/700/api/json',
                 json=load_test_json('queue/waitingitem.json'))
        mock_get(f'{JENKINS_URL}computer/api/json',
                 json=load_test_json('node/computer.json'))
        mock_get(f'{JENKINS_URL}job/Level1_WorkflowJob1/54/api/json',
                 json={'queueId': 699})
        build = item.get_build()
        self.assertIsInstance(build, WorkflowRun)
        self.assertEqual(
            build.url, f'{JENKINS_URL}job/Level1_WorkflowJob1/54/')

    @responses.activate
    def test_get_build_for_buildable_item(self):
        item = QueueItem(self.jx, f'{JENKINS_URL}queue/item/668/')
        mock_get(f'{JENKINS_URL}queue/item/668/api/json',
                 json=load_test_json('queue/buildableitem.json'))
        mock_get(f'{JENKINS_URL}computer/api/json',
                 json=load_test_json('node/computer.json'))
        mock_get(f'{JENKINS_URL}job/Level1_WorkflowJob1/54/api/json',
                 json={'queueId': 667})
        build = item.get_build()
        self.assertIsInstance(build, WorkflowRun)
        self.assertEqual(
            build.url, f'{JENKINS_URL}job/Level1_WorkflowJob1/54/')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
