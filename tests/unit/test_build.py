# encoding: utf-8
from itertools import zip_longest
import unittest

import responses

from jenkinsx import Jenkins
from jenkinsx.build import WorkflowRun
from jenkinsx.item import snake
from jenkinsx.job import WorkflowJob
from .help import load_test_json, mock_get, \
    responses_count, JENKINS_URL


class TestBuild(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.jenkins_json = load_test_json('jenkins/jenkins.json')
        cls.workflow_json = load_test_json('run/workflowrun.json')
        cls.crumb = load_test_json('jenkins/crumb.json')

    def setUp(self):
        mock_get(f'{JENKINS_URL}crumbIssuer/api/json',
                 json=self.crumb)
        mock_get(f'{JENKINS_URL}job/Level1_WorkflowJob1/52/api/json',
                 json=self.workflow_json)
        self.jx = Jenkins(JENKINS_URL, auth=('admin', 'admin'))
        self.build = WorkflowRun(
            self.jx, f'{JENKINS_URL}job/Level1_WorkflowJob1/52/')

    @responses.activate
    def test_console_text(self):
        mock_get(f'{JENKINS_URL}job/Level1_WorkflowJob1/52/consoleText',
                 body='a\nb')
        for given, expected in zip_longest(self.build.console_text(),
                                           [b'a', b'b']):
            with self.subTest(given=given, expected=expected):
                self.assertEqual(given, expected)

    @responses.activate
    def test_progressive_output(self):
        url = f'{JENKINS_URL}job/Level1_WorkflowJob1/52/logText/progressiveText'
        mock_get(url, body='a', headers={
            'X-More-Data': 'True', 'X-Text-Size': '1'})
        mock_get(url, body='b')
        for given, expected in zip_longest(self.build.progressive_output(),
                                           ['a', 'b']):
            with self.subTest(given=given, expected=expected):
                self.assertEqual(given, expected)

    @responses.activate
    def test_get_next_build(self):
        build = self.build.get_next_build()
        self.assertIsNone(build)

    @responses.activate
    def test_get_previous_build(self):
        build = self.build.get_previous_build()
        self.assertIsInstance(build, WorkflowRun)

    @responses.activate
    def test_get_job(self):
        mock_get(f'{JENKINS_URL}api/json?',
                 json=self.jenkins_json)
        job = self.build.get_job()
        self.assertIsInstance(job, WorkflowJob)
        self.assertEqual(
            job.url, f'{JENKINS_URL}job/Level1_WorkflowJob1/')

    @responses.activate
    def test_dynamic_attributes(self):
        dynamic_attrs = {snake(k): v for k, v in
                         self.workflow_json.items()
                         if isinstance(v, (int, str, bool))}
        self.assertEqual(sorted(self.build.attrs),
                         sorted(dynamic_attrs.keys()))
        for key, value in dynamic_attrs.items():
            with self.subTest(value=value):
                self.assertEqual(getattr(self.build, key), value)
        self.assertEqual(responses_count(), 14)
