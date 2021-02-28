import weakref

import pytest
from api4jenkins import Folder, Jenkins
from api4jenkins.exceptions import BadRequestError, ItemNotFoundError
from api4jenkins.item import snake
from api4jenkins.job import WorkflowJob


class TestJenkins:

    def test_init(self, jenkins):
        assert str(jenkins), f'<Jenkins: {jenkins.url}>'

    def test_init_with_token(self, jenkins, monkeypatch, mock_resp):
        data = {'tokenName': 'n',  'tokenValue': 'v',  'tokenUuid': 'u'}
        mock_resp.add('GET', f'{jenkins.url}crumbIssuer/api/json',
                      json=jenkins.crumb)
        req_url = f'{jenkins.url}user/admin/descriptorByName/jenkins.security.ApiTokenProperty/generateNewToken?newTokenName='
        mock_resp.add("POST", req_url, json={'data': data})
        monkeypatch.setattr(weakref, 'finalize', lambda *args: None)
        j = Jenkins(jenkins.url, auth=('admin', 'admin'), token=True)
        assert j._token.name == data['tokenName']
        assert j._token.value == data['tokenValue']

    def test_version(self, jenkins, mock_resp):
        mock_resp.add('GET', jenkins.url, headers={'X-Jenkins': '1.2.3'})
        assert jenkins.version == '1.2.3'

    def test_attrs(self, jenkins):
        expected = []
        for k, v in jenkins.api_json().items():
            if isinstance(v, (int, str, bool, type(None))):
                expected.append(snake(k))
        assert sorted(expected) == sorted(jenkins.dynamic_attrs)

    @pytest.mark.parametrize('name,type_', [('not exist', type(None)),
                                            ('Level1_Folder1', Folder),
                                            ('Level1_Folder1/Level2_Folder1', Folder),
                                            ('Level1_Folder1/Level2_WorkflowJob',
                                             WorkflowJob),
                                            ('Level1_Folder1/not exist', type(None))])
    def test_get_job(self, jenkins, name, type_):
        job = jenkins.get_job(name)
        assert isinstance(job, type_)
        assert isinstance(jenkins[name], type_)

    @pytest.mark.parametrize('headers', [{'X-Error': "A job already exists "
                                          "with the name 'Level1_Folder1'"},
                                         {'X-Error': '@  is an unsafe character'}],
                             ids=['exist', 'unsafe'])
    def test_create_job_fail(self, jenkins, mock_resp, headers):
        mock_resp.add('POST', f'{jenkins.url}createItem',
                      headers=headers, status=400)

        with pytest.raises(BadRequestError, match=r'exists|unsafe'):
            jenkins.create_job('Level1_Folder1', '')

        assert mock_resp.calls[0].response.status_code == 400

    def test_create_job_succ(self, jenkins, mock_resp):
        req_url = f'{jenkins.url}createItem?name=new_job'
        mock_resp.add('POST', req_url)
        jenkins.create_job('new_job', 'xmldata')
        assert mock_resp.calls[0].response.status_code == 200
        assert mock_resp.calls[0].request.url == req_url

    @pytest.mark.parametrize('headers', [{'X-Error': "A job already exists "
                                          "with the name 'Level2_Folder1'"},
                                         {'X-Error': 'No such job: xxxx'}],
                             ids=['job exist', 'no source job'])
    def test_copy_fail(self, jenkins, mock_resp, headers):
        mock_resp.add('POST', f'{jenkins.url}createItem',
                      headers=headers, status=400)
        with pytest.raises(BadRequestError):
            jenkins.copy_job('not exist', 'Level2_Folder1')

    def test_copy_succ(self, jenkins, mock_resp):
        req_url = f'{jenkins.url}createItem?name=new_job&mode=copy&from=src_job'
        mock_resp.add('POST', req_url)
        jenkins.copy_job('src_job', 'new_job')
        assert mock_resp.calls[0].response.status_code == 200
        assert mock_resp.calls[0].request.url == req_url

    def test_delete_job(self, jenkins, mock_resp):
        req_url = f'{jenkins.url}job/Level1_Folder1/doDelete'
        mock_resp.add('POST', req_url)
        jenkins.delete_job('Level1_Folder1')
        assert mock_resp.calls[0].response.status_code == 200
        assert mock_resp.calls[0].request.url == req_url

    @pytest.mark.parametrize('name, exception', [('not exist', ItemNotFoundError),
                                                 ('Level1_Folder1', AttributeError)])
    def test_build_job_fail(self, jenkins, name, exception):
        with pytest.raises(exception):
            jenkins.build_job(name)

    @pytest.mark.parametrize('name, entry, params',
                             [('Level1_WorkflowJob1', 'build', {}),
                              ('Level1_WorkflowJob1',
                               'build?delay=2', {'delay': 2}),
                              ('Level1_WorkflowJob1', 'build?delay=2&token=x',
                               {'delay': 2, 'token': 'x'}),
                              ('Level1_WorkflowJob1',
                               'buildWithParameters?arg1=ab', {'arg1': 'ab'}),
                              ('Level1_WorkflowJob1', 'buildWithParameters?arg1=ab&delay=2&token=x', {
                               'arg1': 'ab', 'delay': 2, 'token': 'x'}),
                              ], ids=['without params', 'with delay', 'with token', 'with params', 'with params+token'])
    def test_build_job_succ(self, jenkins, mock_resp, name, entry, params):
        req_url = f'{jenkins.url}job/{name}/{entry}'
        mock_resp.add('POST', req_url, headers={
                      'Location': f'{jenkins.url}/queue/123'})
        jenkins.build_job(name, **params)
        assert mock_resp.calls[0].request.url == req_url

    @pytest.mark.parametrize('url_entry, name', [('job/job/', 'job'),
                                                 ('job/job/job/job/', 'job/job'),
                                                 ('job/job/job/job', 'job/job')])
    def test__url2name(self, jenkins, url_entry, name):
        assert jenkins._url2name(f'{jenkins.url}{url_entry}') == name

    def test__url2name_value_error(self, jenkins):
        with pytest.raises(ValueError):
            jenkins._url2name('http://0.0.0.1/job/folder1/')

    @pytest.mark.parametrize('name, url_entry', [('', ''),
                                                 ('/job/', 'job/job/'),
                                                 ('job/', 'job/job/'),
                                                 ('/job', 'job/job/'),
                                                 ('job', 'job/job/'),
                                                 ('/job/job/', 'job/job/job/job/'),
                                                 ('job/job/', 'job/job/job/job/'),
                                                 ('/job/job', 'job/job/job/job/'),
                                                 ('job/job', 'job/job/job/job/')])
    def test__name2url(self, jenkins, name, url_entry):
        assert jenkins._name2url(name) == f'{jenkins.url}{url_entry}'

    @pytest.mark.parametrize('status, exist', [(403, True), (200, True),
                                               (404, False), (500, False)])
    def test_exists(self, jenkins, mock_resp, status, exist):
        mock_resp.add('GET', jenkins.url, status=status)
        assert jenkins.exists() == exist

    def test_iter_jobs(self, jenkins):
        assert len(list(jenkins.iter_jobs())) == 2
        assert len(list(jenkins)) == 2
