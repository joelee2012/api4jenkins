import pytest
from api4jenkins.input import PendingInputAction


@pytest.fixture
def pending_input(jenkins):
    raw = {
        "id": "3eaa25d43fac6e39a12c3936942b72c8",
        "proceedText": "Proceed",
        "message": "Is the build okay?",
        "inputs": [],
        "proceedUrl": "/job/input-pipeline/47/wfapi/inputSubmit?inputId=3eaa25d43fac6e39a12c3936942b72c8",
        "abortUrl": "/job/input-pipeline/47/input/3eaa25d43fac6e39a12c3936942b72c8/abort",
        "redirectApprovalUrl": "/job/input-pipeline/47/input/"
    }

    return PendingInputAction(jenkins, raw)


class TestPendingInput:

    def test_access_attrs(self, pending_input):
        assert isinstance(pending_input, PendingInputAction)
        assert pending_input.message == "Is the build okay?"
        assert pending_input.id == "3eaa25d43fac6e39a12c3936942b72c8"
        assert pending_input.proceed_url == "/job/input-pipeline/47/wfapi/inputSubmit?inputId=3eaa25d43fac6e39a12c3936942b72c8"
        assert pending_input.abort_url == "/job/input-pipeline/47/input/3eaa25d43fac6e39a12c3936942b72c8/abort"

    def test_abort(self, pending_input, mock_resp):
        mock_resp.add('POST', f'{pending_input.url}abort')
        pending_input.abort()
        assert mock_resp.calls[0].request.url == f'{pending_input.url}abort'

    @pytest.mark.parametrize('entry, params', [('proceedEmpty', {}), ('submit', {'arg1': 'v'})])
    def test_submit(self, pending_input, mock_resp, entry, params):
        mock_resp.add('POST', f'{pending_input.url}{entry}', json=params)
        pending_input.submit(**params)
