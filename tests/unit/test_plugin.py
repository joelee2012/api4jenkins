# encoding: utf-8
import unittest

import responses

from jenkinsx import Jenkins
from .help import mock_get, load_test_json, JENKINS_URL


class TestPlugin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.plugin_json = load_test_json('plugin/plugin.json')
        cls.crumb = load_test_json('jenkins/crumb.json')

    def setUp(self):
        mock_get(f'{JENKINS_URL}crumbIssuer/api/json',
                 json=self.crumb)
        mock_get(f'{JENKINS_URL}pluginManager/api/json',
                 json=self.plugin_json)
        self.jx = Jenkins(JENKINS_URL, auth=('admin', 'admin'))

    @responses.activate
    def test_get(self):
        self.assertIsNone(self.jx.plugins.get('xyz'))
        plugin = self.jx.plugins.get('git')
        self.assertEqual(
            plugin.url, f'{JENKINS_URL}pluginManager/plugin/git/')
