# encoding: utf-8
import pytest
from api4jenkins.build import WorkflowRun
from api4jenkins.input import PendingInputAction
from respx import MockResponse


class TestBuild:
    def test_console_text(self, workflowrun, respx_mock):
        body = b'a\nb'
        respx_mock.get(f'{workflowrun.url}consoleText').respond(content=body)
        assert list(workflowrun.console_text()) == [
            'a\n', 'b']  # body.split(b'\n')

    def test_progressive_output(self, workflowrun, respx_mock):
        body = ['a', 'b']
        headers = {'X-More-Data': 'True', 'X-Text-Size': '1'}
        req_url = f'{workflowrun.url}logText/progressiveText'
        respx_mock.get(req_url).mock(
            side_effect=[MockResponse(headers=headers, content=body[0], status_code=200), MockResponse(content=body[1], status_code=200)])
        assert list(workflowrun.progressive_output()) == body

    def test_get_next_build(self, workflowrun):
        assert workflowrun.get_next_build() is None

    def test_get_previous_build(self, workflowrun):
        assert isinstance(workflowrun.get_previous_build(), WorkflowRun)

    def test_get_job(self, workflowrun, workflow):
        assert workflow == workflowrun.get_job()

    @pytest.mark.parametrize('action', ['stop', 'term', 'kill'])
    def test_stop_term_kill(self, workflowrun, respx_mock, action):
        req_url = f'{workflowrun.url}{action}'
        respx_mock.post(req_url)
        getattr(workflowrun, action)()
        assert respx_mock.calls[0].request.url == req_url

    def test_get_parameters(self, workflowrun):
        params = workflowrun.get_parameters()
        assert params[0].name == 'parameter1'
        assert params[0].value == 'value1'
        assert params[1].name == 'parameter2'
        assert params[1].value == 'value2'

    def test_get_causes(self, workflowrun):
        causes = workflowrun.get_causes()
        assert causes[0]['shortDescription'] == 'Started by user admin'
        assert causes[1]['shortDescription'] == 'Replayed #1'


class TestWorkflowRun:

    @pytest.mark.parametrize('data, obj', [({"_links": {}}, type(None)),
                                           ({"_links": {"pendingInputActions": 't1'}},
                                            PendingInputAction),
                                           ({"_links": {"pendingInputActions": 't2'}}, PendingInputAction)])
    def test_get_pending_input(self, workflowrun, respx_mock, data, obj):
        respx_mock.get(f'{workflowrun.url}wfapi/describe').respond(json=data)
        if data['_links'] and 'pendingInputActions' in data['_links']:
            if data['_links']['pendingInputActions'] == "t1":
                respx_mock.get(f'{workflowrun.url}wfapi/pendingInputActions').respond(
                    json=[{'abortUrl': '/job/Test%20Workflow/11/input/Ef95dd500ae6ed3b27b89fb852296d12/abort'}])
            elif data['_links']['pendingInputActions'] == "t2":
                respx_mock.get(f'{workflowrun.url}wfapi/pendingInputActions').respond(
                    json=[{'abortUrl': '/jenkins/job/Test%20Workflow/11/input/Ef95dd500ae6ed3b27b89fb852296d12/abort'}])

        assert isinstance(workflowrun.get_pending_input(), obj)

    @pytest.mark.parametrize('data, count', [([], 0),
                                             ([{"url": 'abcd'}], 1)],
                             ids=["empty", "no empty"])
    def test_get_artifacts(self, workflowrun, respx_mock, data, count):
        respx_mock.get(f'{workflowrun.url}wfapi/artifacts').respond(json=data)
        artifacts = workflowrun.get_artifacts()
        assert len(artifacts) == count

    def test_save_artifacts(self, workflowrun, respx_mock, tmp_path):
        respx_mock.get(
            f'{workflowrun.url}artifact/*zip*/archive.zip').respond(content='abc')
        filename = tmp_path / 'my_archive.zip'
        workflowrun.save_artifacts(filename)
        assert filename.exists()
