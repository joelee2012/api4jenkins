# encoding: utf-8
import pytest
from respx import MockResponse

from api4jenkins.build import AsyncWorkflowRun, WorkflowRun
from api4jenkins.input import PendingInputAction


class TestBuild:
    def test_console_text(self, build, respx_mock):
        body = 'a\nb'
        respx_mock.get(f'{build.url}consoleText').respond(content=body)
        assert list(build.console_text()) == body.split('\n')

    def test_progressive_output(self, build, respx_mock):
        body = ['a', 'b']
        headers = {'X-More-Data': 'True', 'X-Text-Size': '1'}
        req_url = f'{build.url}logText/progressiveText'
        respx_mock.get(req_url).mock(
            side_effect=[MockResponse(headers=headers, content=body[0], status_code=200), MockResponse(content=body[1], status_code=200)])
        assert list(build.progressive_output()) == body

    def test_get_next_build(self, build):
        assert build.get_next_build() is None

    def test_get_previous_build(self, build):
        assert isinstance(build.get_previous_build(), WorkflowRun)

    def test_get_job(self, build, job):
        assert job == build.job

    @pytest.mark.parametrize('action', ['stop', 'term', 'kill'])
    def test_stop_term_kill(self, build, respx_mock, action):
        req_url = f'{build.url}{action}'
        respx_mock.post(req_url)
        getattr(build, action)()
        assert respx_mock.calls[0].request.url == req_url

    def test_get_parameters(self, build):
        params = build.get_parameters()
        assert params[0].name == 'parameter1'
        assert params[0].value == 'value1'
        assert params[1].name == 'parameter2'
        assert params[1].value == 'value2'

    def test_get_causes(self, build):
        causes = build.get_causes()
        assert causes[0]['shortDescription'] == 'Started by user admin'
        assert causes[1]['shortDescription'] == 'Replayed #1'


class TestWorkflowRun:

    @pytest.mark.parametrize('data, obj', [({"_links": {}}, type(None)),
                                           ({"_links": {"pendingInputActions": 't1'}},
                                            PendingInputAction),
                                           ({"_links": {"pendingInputActions": 't2'}}, PendingInputAction)])
    def test_get_pending_input(self, build, respx_mock, data, obj):
        respx_mock.get(f'{build.url}wfapi/describe').respond(json=data)
        if data['_links'] and 'pendingInputActions' in data['_links']:
            if data['_links']['pendingInputActions'] == "t1":
                respx_mock.get(f'{build.url}wfapi/pendingInputActions').respond(
                    json=[{'abortUrl': '/job/Test%20Workflow/11/input/Ef95dd500ae6ed3b27b89fb852296d12/abort'}])
            elif data['_links']['pendingInputActions'] == "t2":
                respx_mock.get(f'{build.url}wfapi/pendingInputActions').respond(
                    json=[{'abortUrl': '/jenkins/job/Test%20Workflow/11/input/Ef95dd500ae6ed3b27b89fb852296d12/abort'}])

        assert isinstance(build.get_pending_input(), obj)

    @pytest.mark.parametrize('data, count', [([], 0),
                                             ([{"url": 'abcd'}], 1)],
                             ids=["empty", "no empty"])
    def test_get_artifacts(self, build, respx_mock, data, count):
        respx_mock.get(f'{build.url}wfapi/artifacts').respond(json=data)
        assert len(build.artifacts) == count

    def test_save_artifacts(self, build, respx_mock, tmp_path):
        respx_mock.get(
            f'{build.url}artifact/*zip*/archive.zip').respond(content='abc')
        filename = tmp_path / 'my_archive.zip'
        build.save_artifacts(filename)
        assert filename.exists()


class TestAsyncBuild:
    async def test_console_text(self, async_build, respx_mock):
        body = 'a\nb'
        respx_mock.get(f'{async_build.url}consoleText').respond(content=body)
        output = [line async for line in async_build.console_text()]
        assert output == body.split('\n')

    async def test_progressive_output(self, async_build, respx_mock):
        body = ['a', 'b']
        headers = {'X-More-Data': 'True', 'X-Text-Size': '1'}
        req_url = f'{async_build.url}logText/progressiveText'
        respx_mock.get(req_url).mock(
            side_effect=[MockResponse(headers=headers, content=body[0], status_code=200), MockResponse(content=body[1], status_code=200)])

        assert [line async for line in async_build.progressive_output()] == body

    async def test_get_next_build(self, async_build):
        assert await async_build.get_next_build() is None

    async def test_get_previous_build(self, async_build):
        assert isinstance(await async_build.get_previous_build(), AsyncWorkflowRun)

    async def test_get_job(self, async_build, async_job):
        assert async_job == await async_build.job

    @pytest.mark.parametrize('action', ['stop', 'term', 'kill'])
    async def test_stop_term_kill(self, async_build, respx_mock, action):
        req_url = f'{async_build.url}{action}'
        respx_mock.post(req_url)
        await getattr(async_build, action)()
        assert respx_mock.calls[0].request.url == req_url

    async def test_get_parameters(self, async_build):
        params = await async_build.get_parameters()
        assert params[0].name == 'parameter1'
        assert params[0].value == 'value1'
        assert params[1].name == 'parameter2'
        assert params[1].value == 'value2'

    async def test_get_causes(self, async_build):
        causes = await async_build.get_causes()
        assert causes[0]['shortDescription'] == 'Started by user admin'
        assert causes[1]['shortDescription'] == 'Replayed #1'


class TestAsyncWorkflowRun:

    @pytest.mark.parametrize('data, obj', [({"_links": {}}, type(None)),
                                           ({"_links": {"pendingInputActions": 't1'}},
                                            PendingInputAction),
                                           ({"_links": {"pendingInputActions": 't2'}}, PendingInputAction)])
    async def test_get_pending_input(self, async_build, respx_mock, data, obj):
        respx_mock.get(f'{async_build.url}wfapi/describe').respond(json=data)
        if data['_links'] and 'pendingInputActions' in data['_links']:
            if data['_links']['pendingInputActions'] == "t1":
                respx_mock.get(f'{async_build.url}wfapi/pendingInputActions').respond(
                    json=[{'abortUrl': '/job/Test%20Workflow/11/input/Ef95dd500ae6ed3b27b89fb852296d12/abort'}])
            elif data['_links']['pendingInputActions'] == "t2":
                respx_mock.get(f'{async_build.url}wfapi/pendingInputActions').respond(
                    json=[{'abortUrl': '/jenkins/job/Test%20Workflow/11/input/Ef95dd500ae6ed3b27b89fb852296d12/abort'}])

        assert isinstance(await async_build.get_pending_input(), obj)

    @pytest.mark.parametrize('data, count', [([], 0),
                                             ([{"url": 'abcd'}], 1)],
                             ids=["empty", "no empty"])
    async def test_get_artifacts(self, async_build, respx_mock, data, count):
        respx_mock.get(f'{async_build.url}wfapi/artifacts').respond(json=data)
        artifacts = await async_build.artifacts
        assert len(artifacts) == count

    async def test_save_artifacts(self, async_build, respx_mock, tmp_path):
        respx_mock.get(
            f'{async_build.url}artifact/*zip*/archive.zip').respond(content='abc')
        filename = tmp_path / 'my_archive.zip'
        await async_build.save_artifacts(filename)
        assert filename.exists()
