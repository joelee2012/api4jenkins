# encoding: utf-8
import unittest

import responses

from api4jenkins import Jenkins
from api4jenkins.credential import Credential, Credentials
from api4jenkins.item import snake
from api4jenkins.job import WorkflowJob, Folder
from .help import load_test_json, mock_get, JENKINS_URL


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
        self.jx = Jenkins(JENKINS_URL, auth=('admin', 'admin'))
