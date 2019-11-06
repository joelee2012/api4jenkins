# encoding: utf-8
import unittest

import responses

from jenkinsx import Jenkins
from jenkinsx.credential import Credential
from jenkinsx.item import snake
from tests.unittest.help import load_test_json, mock_get, JENKINS_URL


class TestCredentials(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.credentials_json = load_test_json('credential/credentials.json')
        cls.crumb = load_test_json('jenkins/crumb.json')

    def setUp(self):
        mock_get(f'{JENKINS_URL}crumbIssuer/api/json',
                 json=self.crumb)
        mock_get(f'{JENKINS_URL}credentials/store/system/domain/_/api/json',
                 json=self.credentials_json)
        self.jx = Jenkins(f'{JENKINS_URL}', auth=('admin', 'admin'))

    @responses.activate
    def test_get_none_if_id_not_exist(self):
        self.assertIsNone(self.jx.credentials.get('no exist'))

    @responses.activate
    def test_get_item_if_id_exist(self):
        self.assertIsInstance(self.jx.credentials.get('test-user'), Credential)

    @responses.activate
    def test_get_all_items(self):
        for item in self.jx.credentials:
            with self.subTest(url=item.url):
                self.assertIsInstance(item, Credential)


class TestCredential(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cred_json = load_test_json('credential/user_psw.json')
        cls.crumb = load_test_json('jenkins/crumb.json')

    def setUp(self):
        mock_get(f'{JENKINS_URL}crumbIssuer/api/json',
                 json=self.crumb)
        mock_get(f'{JENKINS_URL}credentials/store/system/domain/_/test-user/api/json',
                 json=self.cred_json)
        self.jx = Jenkins(f'{JENKINS_URL}', auth=('admin', 'admin'))
        self.cred = Credential(
            self.jx, f'{JENKINS_URL}credentials/store/system/domain/_/test-user/')

    @responses.activate
    def test_dynamic_attributes(self):
        dynamic_attrs = {snake(k): v for k, v in
                         self.cred_json.items()
                         if isinstance(v, (int, str, bool))}
        self.assertEqual(sorted(self.cred.attrs),
                         sorted(dynamic_attrs.keys()))
        for key, value in dynamic_attrs.items():
            with self.subTest(value=value):
                self.assertEqual(getattr(self.cred, key), value)
