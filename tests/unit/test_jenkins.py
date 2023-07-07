import weakref

import pytest
from api4jenkins import Jenkins
from api4jenkins.exceptions import BadRequestError, ItemNotFoundError
from api4jenkins.item import new_item, snake
from api4jenkins.job import AsyncFolder, AsyncWorkflowJob, WorkflowJob, Folder


class TestJenkins:

    def test_init(self, jenkins):
        assert str(jenkins), f'<Jenkins: {jenkins.url}>'

    def test_version(self, jenkins, respx_mock):
        respx_mock.get(jenkins.url).respond(headers={'X-Jenkins': '1.2.3'})
        assert jenkins.version == '1.2.3'

    def test_attrs(self, jenkins):
        expected = [
            snake(k)
            for k, v in jenkins.api_json().items()
            if isinstance(v, (int, str, bool, type(None)))
        ]
        assert sorted(expected) == sorted(jenkins.dynamic_attrs)

    @pytest.mark.parametrize('name,type_', [('not exist', type(None)),
                                            ('folder', Folder),
                                            ('folder/pipeline', WorkflowJob),
                                            ('http://0.0.0.0:8080/job/folder/job/pipeline',
                                             WorkflowJob),
                                            ('folder/not exist', type(None))])
    def test_get_job(self, jenkins, name, type_):
        job = jenkins.get_job(name)
        assert isinstance(job, type_)
        assert isinstance(jenkins[name], type_)

    @pytest.mark.parametrize('headers', [{'X-Error': "A job already exists "
                                          "with the name 'folder'"},
                                         {'X-Error': '@  is an unsafe character'}],
                             ids=['exist', 'unsafe'])
    def test_create_job_fail(self, jenkins, respx_mock, headers):
        respx_mock.post(f'{jenkins.url}createItem').respond(
            headers=headers, status_code=400)

        with pytest.raises(BadRequestError, match=r'exists|unsafe'):
            jenkins.create_job('folder', '')

        respx_mock.calls.assert_called_once()

    def test_create_job_succ(self, jenkins, respx_mock):
        req_url = f'{jenkins.url}createItem?name=new_job'
        respx_mock.post(req_url)
        jenkins.create_job('new_job', 'xmldata')
        assert respx_mock.calls[0].response.status_code == 200
        assert respx_mock.calls[0].request.url == req_url

    @pytest.mark.parametrize('headers', [{'X-Error': "A job already exists "
                                          "with the name 'folder2'"},
                                         {'X-Error': 'No such job: xxxx'}],
                             ids=['job exist', 'no source job'])
    def test_copy_fail(self, jenkins, respx_mock, headers):
        respx_mock.post(f'{jenkins.url}createItem').respond(
            headers=headers, status_code=400)
        with pytest.raises(BadRequestError):
            jenkins.copy_job('not exist', 'folder2')

    def test_copy_succ(self, jenkins, respx_mock):
        req_url = f'{jenkins.url}createItem?name=new_job&mode=copy&from=src_job'
        respx_mock.post(req_url)
        jenkins.copy_job('src_job', 'new_job')
        assert respx_mock.calls[0].response.status_code == 200
        assert respx_mock.calls[0].request.url == req_url

    def test_delete_job(self, jenkins, respx_mock):
        req_url = f'{jenkins.url}job/folder/doDelete'
        respx_mock.post(req_url)
        jenkins.delete_job('folder')
        assert respx_mock.calls[0].response.status_code == 200
        assert respx_mock.calls[0].request.url == req_url

    @pytest.mark.parametrize('name, exception', [('not exist', ItemNotFoundError),
                                                 ('folder', AttributeError)])
    def test_build_job_fail(self, jenkins, name, exception):
        with pytest.raises(exception):
            jenkins.build_job(name)

    @pytest.mark.parametrize('name, entry, params',
                             [('folder/job/pipeline', 'build', {}),
                              ('folder/job/pipeline',
                               'build?delay=2', {'delay': 2}),
                              ('folder/job/pipeline', 'build?delay=2&token=x',
                               {'delay': 2, 'token': 'x'}),
                              ('folder/job/pipeline',
                               'buildWithParameters?arg1=ab', {'arg1': 'ab'}),
                              ('folder/job/pipeline', 'buildWithParameters?arg1=ab&delay=2&token=x', {
                               'arg1': 'ab', 'delay': 2, 'token': 'x'}),
                              ], ids=['without params', 'with delay', 'with token', 'with params', 'with params+token'])
    def test_build_job_succ(self, jenkins, respx_mock, name, entry, params):
        req_url = f'{jenkins.url}job/{name}/{entry}'
        respx_mock.post(req_url).respond(
            headers={'Location': f'{jenkins.url}/queue/123'})
        jenkins.build_job(name.replace('/job/', '/'), **params)
        assert respx_mock.calls[0].request.url == req_url

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
    def test_exists(self, jenkins, respx_mock, status, exist):
        respx_mock.get(jenkins.url).respond(status)
        assert jenkins.exists() == exist

    def test_iter_jobs(self, jenkins):
        assert len(list(jenkins.iter_jobs(1))) == 5
        assert len(list(jenkins)) == 5
        assert len(list(jenkins(1))) == 5

    def test_no_class_for_item(self, jenkins):
        with pytest.raises(AttributeError) as e:
            new_item(jenkins, 'api4jenkins.job', {
                     '_class': 'NotExistItem', 'url': 'abc'})

    def test_move(self, jenkins, folder, respx_mock):
        req_url = f'{folder.url}move/move'
        respx_mock.post(req_url).respond(
            headers={'Location': f'{jenkins.url}job/folder2/job/folder/'})
        jenkins.move_job('folder', 'folder2')
        assert respx_mock.calls[0].request.url == req_url

    def test_rename(self, jenkins, folder, respx_mock):
        req_url = f'{folder.url}confirmRename?newName=folder2'
        respx_mock.post(req_url).respond(
            headers={'Location': f'{jenkins.url}job/folder2'})
        jenkins.rename_job('folder', 'folder2')
        assert respx_mock.calls[0].request.url == req_url

    def test_dumplicate(self, jenkins, folder, respx_mock):
        respx_mock.get(f'{folder.url}config.xml')
        req_url = f'{jenkins.url}createItem?name=folder2'
        respx_mock.post(req_url)
        jenkins.duplicate_job('folder', 'folder2')
        assert respx_mock.calls[1].request.url == req_url


class TestAsyncJenkins:

    async def test_init(self, async_jenkins):
        assert str(async_jenkins), f'<AsyncJenkins: {async_jenkins.url}>'

    async def test_version(self, async_jenkins, respx_mock):
        respx_mock.get(async_jenkins.url).respond(
            headers={'X-Jenkins': '1.2.3'})
        assert await async_jenkins.version == '1.2.3'

    async def test_attrs(self, async_jenkins):
        data = await async_jenkins.api_json()
        expected = [
            snake(k)
            for k, v in data.items()
            if isinstance(v, (int, str, bool, type(None)))
        ]
        assert sorted(expected) == sorted(await async_jenkins.dynamic_attrs)

    @pytest.mark.parametrize('name,type_', [('not exist', type(None)),
                                            ('folder', AsyncFolder),
                                            ('folder/pipeline', AsyncWorkflowJob),
                                            ('http://0.0.0.0:8080/job/folder/job/pipeline',
                                             AsyncWorkflowJob),
                                            ('folder/not exist', type(None))])
    async def test_get_job(self, async_jenkins, name, type_):
        job = await async_jenkins.get_job(name)
        assert isinstance(job, type_)
        assert isinstance(await async_jenkins[name], type_)

    @pytest.mark.parametrize('headers', [{'X-Error': "A job already exists "
                                          "with the name 'folder'"},
                                         {'X-Error': '@  is an unsafe character'}],
                             ids=['exist', 'unsafe'])
    async def test_create_job_fail(self, async_jenkins, respx_mock, headers):
        respx_mock.post(f'{async_jenkins.url}createItem').respond(
            headers=headers, status_code=400)

        with pytest.raises(BadRequestError, match=r'exists|unsafe'):
            await async_jenkins.create_job('folder', '')

        respx_mock.calls.assert_called_once()

    async def test_create_job_succ(self, async_jenkins, respx_mock):
        req_url = f'{async_jenkins.url}createItem?name=new_job'
        respx_mock.post(req_url)
        await async_jenkins.create_job('new_job', 'xmldata')
        assert respx_mock.calls[0].response.status_code == 200
        assert respx_mock.calls[0].request.url == req_url

    @pytest.mark.parametrize('headers', [{'X-Error': "A job already exists "
                                          "with the name 'folder2'"},
                                         {'X-Error': 'No such job: xxxx'}],
                             ids=['job exist', 'no source job'])
    async def test_copy_fail(self, async_jenkins, respx_mock, headers):
        respx_mock.post(f'{async_jenkins.url}createItem').respond(
            headers=headers, status_code=400)
        with pytest.raises(BadRequestError):
            await async_jenkins.copy_job('not exist', 'folder2')

    async def test_copy_succ(self, async_jenkins, respx_mock):
        req_url = f'{async_jenkins.url}createItem?name=new_job&mode=copy&from=src_job'
        respx_mock.post(req_url)
        await async_jenkins.copy_job('src_job', 'new_job')
        assert respx_mock.calls[0].response.status_code == 200
        assert respx_mock.calls[0].request.url == req_url

    async def test_delete_job(self, async_jenkins, respx_mock):
        req_url = f'{async_jenkins.url}job/folder/doDelete'
        respx_mock.post(req_url)
        await async_jenkins.delete_job('folder')
        assert respx_mock.calls[0].response.status_code == 200
        assert respx_mock.calls[0].request.url == req_url

    @pytest.mark.parametrize('name, exception', [('not exist', ItemNotFoundError),
                                                 ('folder', AttributeError)])
    async def test_build_job_fail(self, async_jenkins, name, exception):
        with pytest.raises(exception):
            await async_jenkins.build_job(name)

    @pytest.mark.parametrize('name, entry, params',
                             [('folder/job/pipeline', 'build', {}),
                              ('folder/job/pipeline',
                               'build?delay=2', {'delay': 2}),
                              ('folder/job/pipeline', 'build?delay=2&token=x',
                               {'delay': 2, 'token': 'x'}),
                              ('folder/job/pipeline',
                               'buildWithParameters?arg1=ab', {'arg1': 'ab'}),
                              ('folder/job/pipeline', 'buildWithParameters?arg1=ab&delay=2&token=x', {
                               'arg1': 'ab', 'delay': 2, 'token': 'x'}),
                              ], ids=['without params', 'with delay', 'with token', 'with params', 'with params+token'])
    async def test_build_job_succ(self, async_jenkins, respx_mock, name, entry, params):
        req_url = f'{async_jenkins.url}job/{name}/{entry}'
        respx_mock.post(req_url).respond(
            headers={'Location': f'{async_jenkins.url}/queue/123'})
        await async_jenkins.build_job(name.replace('/job/', '/'), **params)
        assert respx_mock.calls[0].request.url == req_url

    @pytest.mark.parametrize('url_entry, name', [('job/job/', 'job'),
                                                 ('job/job/job/job/', 'job/job'),
                                                 ('job/job/job/job', 'job/job')])
    async def test__url2name(self, async_jenkins, url_entry, name):
        assert async_jenkins._url2name(
            f'{async_jenkins.url}{url_entry}') == name

    async def test__url2name_value_error(self, async_jenkins):
        with pytest.raises(ValueError):
            async_jenkins._url2name('http://0.0.0.1/job/folder1/')

    @pytest.mark.parametrize('name, url_entry', [('', ''),
                                                 ('/job/', 'job/job/'),
                                                 ('job/', 'job/job/'),
                                                 ('/job', 'job/job/'),
                                                 ('job', 'job/job/'),
                                                 ('/job/job/', 'job/job/job/job/'),
                                                 ('job/job/', 'job/job/job/job/'),
                                                 ('/job/job', 'job/job/job/job/'),
                                                 ('job/job', 'job/job/job/job/')])
    async def test__name2url(self, async_jenkins, name, url_entry):
        assert async_jenkins._name2url(
            name) == f'{async_jenkins.url}{url_entry}'

    @pytest.mark.parametrize('status, exist', [(403, True), (200, True),
                                               (404, False), (500, False)])
    async def test_exists(self, async_jenkins, respx_mock, status, exist):
        respx_mock.get(async_jenkins.url).respond(status)
        assert await async_jenkins.exists() == exist

    async def test_iter_jobs(self, async_jenkins):
        assert len([j async for j in async_jenkins.iter_jobs()]) == 5
        assert len([j async for j in async_jenkins]) == 5

    async def test_no_class_for_item(self, async_jenkins):
        with pytest.raises(AttributeError) as e:
            new_item(async_jenkins, 'api4jenkins.job', {
                     '_class': 'NotExistItem', 'url': 'abc'})

    async def test_move(self, async_jenkins, async_folder, respx_mock):
        req_url = f'{async_folder.url}move/move'
        respx_mock.post(req_url).respond(
            headers={'Location': f'{async_jenkins.url}job/folder2/job/folder/'})
        await async_jenkins.move_job('folder', 'folder2')
        assert respx_mock.calls[0].request.url == req_url

    async def test_rename(self, async_jenkins, async_folder, respx_mock):
        req_url = f'{async_folder.url}confirmRename?newName=folder2'
        respx_mock.post(req_url).respond(
            headers={'Location': f'{async_jenkins.url}job/folder2'})
        await async_jenkins.rename_job('folder', 'folder2')
        assert respx_mock.calls[0].request.url == req_url

    async def test_dumplicate(self, async_jenkins, async_folder, respx_mock):
        respx_mock.get(f'{async_folder.url}config.xml')
        req_url = f'{async_jenkins.url}createItem?name=folder2'
        respx_mock.post(req_url)
        await async_jenkins.duplicate_job('folder', 'folder2')
        assert respx_mock.calls[1].request.url == req_url
