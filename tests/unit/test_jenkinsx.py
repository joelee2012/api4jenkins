# encoding: utf-8
import unittest

import responses

from jenkinsx import Jenkins
from jenkinsx.exceptions import ItemNotFoundError, \
    AuthenticationError, BadRequestError
from jenkinsx.item import snake
from jenkinsx.job import Folder
from jenkinsx.user import ApiToken
from .help import mock_get, load_test_json, \
    mock_post, remove_get, replace_get, JENKINS_URL


# logging.basicConfig(level=logging.DEBUG)
class TestJenkins(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.jenkins_json = load_test_json('jenkins/jenkins.json')
        cls.folder_json = load_test_json('job/folder.json')
        cls.crumb = load_test_json('jenkins/crumb.json')

    def setUp(self):
        mock_get(f'{JENKINS_URL}crumbIssuer/api/json',
                 json=self.crumb)
        mock_get(f'{JENKINS_URL}api/json', json=self.jenkins_json)
        mock_get(f'{JENKINS_URL}job/Level1_Folder1/api/json',
                 json=self.folder_json)
        self.jx = Jenkins(f'{JENKINS_URL}', auth=('admin', 'admin'))

    @responses.activate
    def test_init_with_invalid_auth(self):
        remove_get(f'{JENKINS_URL}crumbIssuer/api/json')
        mock_get(f'{JENKINS_URL}crumbIssuer/api/json', status=401)
        jx = Jenkins(f'{JENKINS_URL}', auth=('admin', 'admin'))
        with self.assertRaises(AuthenticationError):
            jx.api_json()

    def test_init_with_password(self):
        self.assertIsInstance(self.jx, Jenkins)
        self.assertEqual(str(self.jx), f'<Jenkins: {JENKINS_URL}>')
        self.assertEqual(self.jx.url, JENKINS_URL)
        self.assertIsNone(self.jx._crumb)
        self.assertIsNone(self.jx._token)

    @responses.activate
    def test_init_with_token(self):
        data = {'tokenName': 'mock-token-name',
                'tokenValue': 'mock-token-value',
                'tokenUuid': 'mock-token-uuid'}
        token = ApiToken(data['tokenName'],
                         data['tokenUuid'], data['tokenValue'])
        mock_post(f'{JENKINS_URL}user/admin/'
                  'descriptorByName/jenkins.security.ApiTokenProperty/'
                  'generateNewToken?newTokenName=',
                  json={'data': data})
        mock_get(JENKINS_URL)
        with unittest.mock.patch('weakref.finalize') as mock_fin:
            mock_fin.side_effect = lambda *args: None
            jx = Jenkins(JENKINS_URL,
                         auth=('admin', 'admin'), token=True)
        self.assertTrue(jx.exists())
        self.assertEqual(jx.url, JENKINS_URL)
        self.assertEqual(jx._crumb, self.crumb)
        self.assertEqual(jx._token, token)

    @responses.activate
    def test_dynamic_attributes(self):
        dynamic_attrs = {snake(k): v for k, v in self.jenkins_json.items()
                         if isinstance(v, (int, str, bool))}
        self.assertEqual(sorted(self.jx.attrs),
                         sorted(dynamic_attrs.keys()))
        for key, value in dynamic_attrs.items():
            with self.subTest(value=value):
                self.assertEqual(getattr(self.jx, key), value)

    @responses.activate
    def test_get_job_when_not_found(self):
        not_found = self.jx.get_job('Level1_Folder1/notfound')
        self.assertIsNone(not_found)

    @responses.activate
    def test_get_job(self):
        level1_folder1 = self.jx.get_job('Level1_Folder1')
        self.assertEqual(self.jx._crumb, self.crumb)
        self.assertIsNone(self.jx._token)
        self.assertIsInstance(level1_folder1, Folder)
        self.assertEqual(str(level1_folder1),
                         f'<Folder: {JENKINS_URL}job/Level1_Folder1/>')
        level2_folder1 = self.jx.get_job('Level1_Folder1/Level2_Folder1')
        self.assertIsInstance(level2_folder1, Folder)
        self.assertEqual(str(level2_folder1),
                         f'<Folder: {JENKINS_URL}job/Level1_Folder1/'
                         'job/Level2_Folder1/>')

    @responses.activate
    def test_iter_jobs(self):
        replace_get(f'{JENKINS_URL}api/json',
                    json=load_test_json('jenkins/jenkins_all_jobs.json'))
        jobs = list(self.jx.iter_jobs())
        self.assertEqual(len(jobs), 6)

    @responses.activate
    def test_create_job_when_exists(self):
        mock_post(
            f'{JENKINS_URL}job/Level1_Folder1/createItem',
            headers={
                'X-Error': "A job already exists with"
                " the name 'Level2_Folder1'"},
            status=400)
        with self.assertRaises(BadRequestError):
            self.jx.create_job('Level1_Folder1/Level2_Folder1', '')

    @responses.activate
    def test_create_job_when_name_illegal(self):
        mock_post(
            f'{JENKINS_URL}job/Level1_Folder1/createItem',
            headers={'X-Error': '@  is an unsafe character'},
            status=400)
        with self.assertRaisesRegex(BadRequestError,
                                    '@  is an unsafe character'):
            self.jx.create_job('Level1_Folder1/Level2@new', '')

    @responses.activate
    def test_create_job(self):
        mock_post(
            f'{JENKINS_URL}job/Level1_Folder1/createItem?name=Levevl2_new',
            match_querystring=True)
        self.jx.create_job('Level1_Folder1/Levevl2_new', '')

    @responses.activate
    def test_delete_job(self):
        mock_post(f'{JENKINS_URL}job/Level1_Folder1/'
                  'job/Level2_Folder1/doDelete',
                  match_querystring=True)
        self.jx.delete_job('Level1_Folder1/Level2_Folder1')

    @responses.activate
    def test_build_job_when_not_found(self):
        with self.assertRaisesRegex(ItemNotFoundError,
                                    'No such job: '
                                    'Level1_Folder1/Level2_notFound'):
            self.jx.build_job('Level1_Folder1/Level2_notFound')

    @responses.activate
    def test_build_job_when_job_is_unbuildable(self):
        with self.assertRaisesRegex(AttributeError,
                                    "'Folder' object has no attribute 'build'"):
            self.jx.build_job('Level1_Folder1')

    def test_url2full_name(self):
        with self.assertRaises(ValueError):
            self.jx._url2name('http://0.0.0.1/job/folder1/')
        full_name = self.jx._url2name(f'{JENKINS_URL}job/job/')
        self.assertEqual(full_name, '/job/')
        full_name = self.jx._url2name(
            f'{JENKINS_URL}job/job/job/job/')
        self.assertEqual(full_name, '/job/job/')
        full_name = self.jx._url2name(f'{JENKINS_URL}job/job/job/job')
        self.assertEqual(full_name, '/job/job')

    def test_full_name2url(self):
        self.assertEqual(self.jx._name2url(''), self.jx.url)
        for name in ['/job/', 'job/', '/job', 'job']:
            with self.subTest(name=name):
                self.assertEqual(self.jx._name2url(name),
                                 f'{JENKINS_URL}job/job/')
        for name in ['/job/job/', 'job/job/', '/job/job', 'job/job']:
            with self.subTest(name=name):
                self.assertEqual(self.jx._name2url(name),
                                 f'{JENKINS_URL}job/job/job/job/')

    @responses.activate
    def test_api_json(self):
        json = self.jx.api_json()
        self.assertEqual(json, self.jenkins_json)

    @responses.activate
    def test_exists(self):
        for status in [401, 403]:
            remove_get(JENKINS_URL)
            mock_get(JENKINS_URL, status=status)
            with self.subTest(status=status):
                self.assertTrue(self.jx.exists())

        for status in [404, 503]:
            remove_get(JENKINS_URL)
            mock_get(JENKINS_URL, status=status)
            with self.subTest(status=status):
                self.assertFalse(self.jx.exists())

    @responses.activate
    def test_handle_req(self):
        json = self.jx.handle_req('GET', 'api/json').json()
        self.assertEqual(json, self.jenkins_json)
