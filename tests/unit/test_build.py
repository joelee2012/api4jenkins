# encoding: utf-8
import pytest
from api4jenkins.build import WorkflowRun
from api4jenkins.input import PendingInputAction


class TestBuild:
    def test_console_text(self, workflowrun, mock_resp):
        body = b'a\nb'
        mock_resp.add('GET', f'{workflowrun.url}consoleText', body=body)
        assert list(workflowrun.console_text()) == body.split(b'\n')

    def test_progressive_output(self, workflowrun, mock_resp):
        body = ['a', 'b']
        headers = {'X-More-Data': 'True', 'X-Text-Size': '1'}
        req_url = f'{workflowrun.url}logText/progressiveText'
        mock_resp.add('GET', req_url, headers=headers, body=body[0])
        mock_resp.add('GET', req_url, body=body[1])
        assert list(workflowrun.progressive_output()) == body

    def test_get_next_build(self, workflowrun):
        assert workflowrun.get_next_build() is None

    def test_get_previous_build(self, workflowrun):
        assert isinstance(workflowrun.get_previous_build(), WorkflowRun)

    def test_get_job(self, workflowrun, workflow):
        assert workflow == workflowrun.get_job()

    @pytest.mark.parametrize('action', ['stop', 'term', 'kill'])
    def test_stop_term_kill(self, workflowrun, mock_resp, action):
        req_url = f'{workflowrun.url}{action}'
        mock_resp.add('POST', req_url)
        getattr(workflowrun, action)()
        assert mock_resp.calls[0].request.url == req_url

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
                                           ({"_links": {"pendingInputActions": 'x'}}, PendingInputAction)])
    def test_get_pending_input(self, workflowrun, mock_resp, data, obj):
        mock_resp.add('GET', f'{workflowrun.url}wfapi/describe', json=data)
        if data['_links']:
            mock_resp.add('GET', f'{workflowrun.url}wfapi/pendingInputActions',
                          json=[{'abortUrl': 'x'}])
        assert isinstance(workflowrun.get_pending_input(), obj)

    @pytest.mark.parametrize('data, count', [([], 0),
                                             ([{"url": 'abcd'}], 1)],
                             ids=["empty", "no empty"])
    def test_get_artifacts(self, workflowrun, mock_resp, data, count):
        mock_resp.add('GET', f'{workflowrun.url}wfapi/artifacts', json=data)
        artifacts = workflowrun.get_artifacts()
        assert len(artifacts) == count

    def test_save_artifacts(self, workflowrun, mock_resp, tmp_path):
        mock_resp.add(
            'GET', f'{workflowrun.url}artifact/*zip*/archive.zip', body='abc')
        filename = tmp_path / 'my_archive.zip'
        workflowrun.save_artifacts(filename)
        assert filename.exists()
