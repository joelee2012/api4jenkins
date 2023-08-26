# encoding: utf-8
import pytest
from api4jenkins.build import AsyncWorkflowRun, WorkflowRun
from api4jenkins.item import snake


class TestFolder:

    def test_parent(self, folder, jenkins, job):
        assert job.parent == folder
        assert folder.parent == jenkins

    @pytest.mark.parametrize('req, xml, body',
                             [('GET', None, '<xml/>'), ('POST', '<xml/>', '')],
                             ids=['get', 'set'])
    def test_configure(self, folder, respx_mock, req, xml, body):
        req_url = f'{folder.url}config.xml'
        respx_mock.route(method=req, url=req_url).respond(content=body)
        text = folder.configure(xml)
        assert respx_mock.calls[0].request.url == req_url


class TestWorkflowMultiBranchProject:

    def test_scan(self, multi_job, respx_mock):
        req_url = f'{multi_job.url}build?delay=0'
        respx_mock.post(req_url)
        multi_job.scan()
        assert respx_mock.calls[0].request.url == req_url

    def test_get_scan_log(self, multi_job, respx_mock):
        body = 'a\nb'
        respx_mock.get(
            f'{multi_job.url}indexing/consoleText').respond(content=body)
        assert list(multi_job.get_scan_log()) == body.split('\n')


class TestProject:

    @pytest.mark.parametrize('number, obj',
                             [(52, WorkflowRun), (100, type(None))],
                             ids=['exist', 'not exist'])
    def test_get_build(self, job, number, obj):
        build = job.get_build(number)
        assert isinstance(build, obj)
        build = job.get_build(f'#{number}')
        assert isinstance(build, obj)

    @pytest.mark.parametrize('key', ['firstBuild', 'lastBuild', 'lastCompletedBuild',
                                     'lastFailedBuild', 'lastStableBuild', 'lastUnstableBuild',
                                     'lastSuccessfulBuild', 'lastUnsuccessfulBuild'])
    def test_get_(self, job, key):
        build = getattr(job, snake(f'get_{key}'))()
        assert isinstance(build, WorkflowRun)
        assert build.url == job.api_json()[key]['url']

    def test_iter_builds(self, job):
        builds = list(job.iter_builds())
        assert len(builds) == 8

    @pytest.mark.parametrize('action', ['enable', 'disable'])
    def test_enable_disable(self, job, respx_mock, action):
        req_url = f'{job.url}{action}'
        respx_mock.post(req_url)
        getattr(job, action)()
        assert respx_mock.calls[0].request.url == req_url

    def test_building(self, job):
        assert job.building is False


class TestAsyncFolder:

    async def test_parent(self, async_folder, async_jenkins, async_job):
        assert await async_folder.parent == async_jenkins
        assert await async_job.parent == async_folder

    @pytest.mark.parametrize('req, xml, body',
                             [('GET', None, '<xml/>'), ('POST', '<xml/>', '')],
                             ids=['get', 'set'])
    async def test_configure(self, async_folder, req, xml, body, respx_mock):
        req_url = f'{async_folder.url}config.xml'
        respx_mock.route(method=req, url=req_url).respond(content=body)
        text = await async_folder.configure(xml)
        assert respx_mock.calls[0].request.url == req_url


class TestAsyncWorkflowMultiBranchProject:

    async def test_scan(self, async_multi_job, respx_mock):
        req_url = f'{async_multi_job.url}build?delay=0'
        respx_mock.post(req_url)
        await async_multi_job.scan()
        assert respx_mock.calls[0].request.url == req_url

    async def test_get_scan_log(self, async_multi_job, respx_mock):
        body = 'a\nb'
        respx_mock.get(
            f'{async_multi_job.url}indexing/consoleText').respond(content=body)
        assert [line async for line in async_multi_job.get_scan_log()] == body.split('\n')


class TestAsyncProject:

    @pytest.mark.parametrize('number, obj',
                             [(52, AsyncWorkflowRun), (100, type(None))],
                             ids=['exist', 'not exist'])
    async def test_get_build(self, async_job, number, obj):
        build = await async_job.get_build(number)
        assert isinstance(build, obj)
        build = await async_job.get_build(f'#{number}')
        assert isinstance(build, obj)

    @pytest.mark.parametrize('key', ['firstBuild', 'lastBuild', 'lastCompletedBuild',
                                     'lastFailedBuild', 'lastStableBuild', 'lastUnstableBuild',
                                     'lastSuccessfulBuild', 'lastUnsuccessfulBuild'])
    async def test_get_(self, async_job, key):
        build = await getattr(async_job, snake(f'get_{key}'))()
        job_json = await async_job.api_json()
        assert isinstance(build, AsyncWorkflowRun)
        assert build.url == job_json[key]['url']

    async def test_iter_builds(self, async_job):
        builds = [b async for b in async_job.iter_builds()]
        assert len(builds) == 8

    @pytest.mark.parametrize('action', ['enable', 'disable'])
    async def test_enable_disable(self, async_job, respx_mock, action):
        req_url = f'{async_job.url}{action}'
        respx_mock.post(req_url)
        await getattr(async_job, action)()
        assert respx_mock.calls[0].request.url == req_url

    async def test_building(self, async_job):
        assert await async_job.building is False
