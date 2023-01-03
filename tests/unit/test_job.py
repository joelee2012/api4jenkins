# encoding: utf-8
import pytest
from api4jenkins.build import WorkflowRun
from api4jenkins.exceptions import BadRequestError
from api4jenkins.item import snake
from api4jenkins.job import Folder, WorkflowJob


class TestFolder:

    @pytest.mark.parametrize('headers', [{'X-Error': "A job already exists "
                                          "with the name 'Level1_Folder1'"},
                                         {'X-Error': '@  is an unsafe character'}],
                             ids=['exist', 'unsafe'])
    def test_create_fail(self, folder, respx_mock, headers):
        respx_mock.post(f'{folder.url}createItem').respond(
            headers=headers, status_code=400)

        with pytest.raises(BadRequestError, match=r'exists|unsafe'):
            folder.create('Level2_Folder1', '')

        assert respx_mock.calls[0].response.status_code == 400

    def test_create_succ(self, folder, respx_mock):
        req_url = f'{folder.url}createItem?name=new_job'
        respx_mock.post(req_url)
        folder.create('new_job', 'xmldata')
        assert respx_mock.calls[0].response.status_code == 200
        assert respx_mock.calls[0].request.url == req_url

    @pytest.mark.parametrize('name,type_', [('not exist', type(None)),
                                            ('Level2_Folder1', Folder),
                                            ('Level2_WorkflowJob', WorkflowJob)])
    def test_get(self, folder, name, type_):
        job = folder.get(name)
        assert isinstance(job, type_)
        assert isinstance(folder[name], type_)

    def test_iter_jobs(self, folder):
        assert len(list(folder.iter())) == 4
        assert len(list(folder)) == 4

    @pytest.mark.parametrize('headers', [{'X-Error': "A job already exists "
                                          "with the name 'Level2_Folder1'"},
                                         {'X-Error': 'No such job: xxxx'}],
                             ids=['job exist', 'no source job'])
    def test_copy_fail(self, folder, respx_mock, headers):
        respx_mock.post(f'{folder.url}createItem').respond(
            headers=headers, status_code=400)
        with pytest.raises(BadRequestError):
            folder.copy('not exist', 'Level2_Folder1')

    def test_copy_succ(self, folder, respx_mock):
        req_url = f'{folder.url}createItem?name=new_job&mode=copy&from=src_job'
        respx_mock.post(req_url)
        folder.copy('src_job', 'new_job')
        assert respx_mock.calls[0].response.status_code == 200
        assert respx_mock.calls[0].request.url == req_url

    def test_move(self, folder, respx_mock):
        new_location = 'Level1_Folder2'
        headers = {'Location': f'{folder.jenkins.url}job/{new_location}/'
                   'job/Level1_Folder1/'}
        req_url = f'{folder.url}move/move'
        respx_mock.post(req_url).respond(headers=headers)
        folder.move(new_location)
        assert respx_mock.calls[0].request.url == req_url
        assert folder.url == headers['Location']

    def test_rename(self, folder, respx_mock):
        new_name = 'Level1_Folder3'
        headers = {'Location': f'{folder.jenkins.url}job/{new_name}/'}
        req_url = f'{folder.url}confirmRename?newName=Level1_Folder3'
        respx_mock.post(req_url).respond(headers=headers)
        folder.rename(new_name)
        assert respx_mock.calls[0].request.url == req_url
        assert folder.url == headers['Location']

    def test_parent(self, folder, jenkins, monkeypatch):
        folder2 = folder.get('Level2_Folder1')
        # monkeypatch.setattr(folder2, 'full_name',
        #                     'Level1_Folder1/Level2_Folder1')
        assert folder.parent == jenkins
        assert folder2.parent == folder
        assert folder2.parent.parent == jenkins

    def test_delete(self, folder, respx_mock):
        req_url = f'{folder.url}doDelete'
        respx_mock.post(req_url)
        folder.delete()
        assert respx_mock.calls[0].response.status_code == 200
        assert respx_mock.calls[0].request.url == req_url

    @pytest.mark.parametrize('req, xml, body',
                             [('GET', None, '<xml/>'), ('POST', '<xml/>', '')],
                             ids=['get', 'set'])
    def test_configure(self, folder, respx_mock, req, xml, body):
        req_url = f'{folder.url}config.xml'
        respx_mock.route(method=req, url=req_url).respond(content=body)
        text = folder.configure(xml)
        assert respx_mock.calls[0].request.url == req_url
        if req == 'GET':
            assert text == body


class TestWorkflowMultiBranchProject:

    def test_scan(self, multibranchproject, respx_mock):
        req_url = f'{multibranchproject.url}build?delay=0'
        respx_mock.post(req_url)
        multibranchproject.scan()
        assert respx_mock.calls[0].request.url == req_url

    def test_get_scan_log(self, multibranchproject, respx_mock):
        body = 'a\nb'
        respx_mock.get(
            f'{multibranchproject.url}indexing/consoleText').respond(content=body)
        assert list(multibranchproject.get_scan_log()) == body.split('\n')


class TestProject:

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
    def test_build(self, pipeline, respx_mock, name, entry, params):
        req_url = f'{pipeline.url}{entry}'
        respx_mock.post(req_url).respond(
            headers={'Location': f'{pipeline.jenkins.url}/queue/123'})
        pipeline.build(**params)
        assert respx_mock.calls[0].request.url == req_url

    @pytest.mark.parametrize('number, obj',
                             [(52, WorkflowRun), (100, type(None))],
                             ids=['exist', 'not exist'])
    def test_get_build(self, pipeline, number, obj):
        build = pipeline.get_build(number)
        assert isinstance(build, obj)
        build = pipeline.get_build(f'#{number}')
        assert isinstance(build, obj)

    @pytest.mark.parametrize('key', ['firstBuild', 'lastBuild', 'lastCompletedBuild',
                                     'lastFailedBuild', 'lastStableBuild', 'lastUnstableBuild',
                                     'lastSuccessfulBuild', 'lastUnsuccessfulBuild'])
    def test_get_(self, pipeline, key):
        build = getattr(pipeline, snake(f'get_{key}'))()
        if key == 'lastUnstableBuild':
            assert build is None
        else:
            assert isinstance(build, WorkflowRun)
            assert build.url == pipeline.api_json()[key]['url']

    def test_iter_builds(self, pipeline):
        builds = list(pipeline.iter_builds())
        assert len(builds) == 8

    @pytest.mark.parametrize('action', ['enable', 'disable'])
    def test_enable_disable(self, pipeline, respx_mock, action):
        req_url = f'{pipeline.url}{action}'
        respx_mock.post(req_url)
        getattr(pipeline, action)()
        assert respx_mock.calls[0].request.url == req_url

    def test_building(self, pipeline):
        assert pipeline.building is False
