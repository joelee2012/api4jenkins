# encoding: utf-8

from api4jenkins.build import WorkflowRun



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
