import pytest
from api4jenkins.input import AsyncPendingInputAction, PendingInputAction, _make_input_params


raw = {
    "id": "3eaa25d43fac6e39a12c3936942b72c8",
    "proceedText": "Proceed",
    "message": "Is the build okay?",
    "inputs": [],
    "proceedUrl": "/job/input-pipeline/47/wfapi/inputSubmit?inputId=3eaa25d43fac6e39a12c3936942b72c8",
    "abortUrl": "/job/input-pipeline/47/input/3eaa25d43fac6e39a12c3936942b72c8/abort",
    "redirectApprovalUrl": "/job/input-pipeline/47/input/"
}
@pytest.fixture
def pending_input(jenkins):
    return PendingInputAction(jenkins, raw)

@pytest.fixture
def async_pending_input(async_jenkins):
    return AsyncPendingInputAction(async_jenkins, raw)
# @pytest.mark.skip
class TestPendingInput:

    def test_access_attrs(self, pending_input):
        assert isinstance(pending_input, PendingInputAction)
        assert pending_input.message == "Is the build okay?"
        assert pending_input.id == "3eaa25d43fac6e39a12c3936942b72c8"
        assert pending_input.proceed_url == "/job/input-pipeline/47/wfapi/inputSubmit?inputId=3eaa25d43fac6e39a12c3936942b72c8"
        assert pending_input.abort_url == "/job/input-pipeline/47/input/3eaa25d43fac6e39a12c3936942b72c8/abort"

    def test_abort(self, pending_input, respx_mock):
        respx_mock.post(f'{pending_input.url}abort')
        pending_input.abort()
        assert respx_mock.calls[0].request.url == f'{pending_input.url}abort'

    def test_submit_empty(self, pending_input, respx_mock):
        respx_mock.post(f'{pending_input.url}proceedEmpty')
        pending_input.submit()
        assert respx_mock.calls[0].request.url == f'{pending_input.url}proceedEmpty'

    def test_submit_arg(self, pending_input, respx_mock):
        pending_input.raw['inputs'] = [{'name': 'arg1'}]
        respx_mock.post(f'{pending_input.url}submit').respond(
            json={'arg1': 'x'})
        pending_input.submit(arg1='x')
        assert respx_mock.calls[0].request.url == f'{pending_input.url}submit'

    def test_submit_empty_with_arg(self, pending_input):
        pending_input.raw['inputs'] = []
        with pytest.raises(TypeError):
            pending_input.submit(arg1='x')

    def test_submit_wrong_arg(self, pending_input):
        pending_input.raw['inputs'] = [{'name': 'arg1'}]
        with pytest.raises(TypeError):
            pending_input.submit(arg2='x')


class TestAsyncPendingInput:

    async def test_access_attrs(self, async_pending_input):
        assert isinstance(async_pending_input, AsyncPendingInputAction)
        assert await async_pending_input.message == "Is the build okay?"
        assert await async_pending_input.id == "3eaa25d43fac6e39a12c3936942b72c8"
        assert await async_pending_input.proceed_url == "/job/input-pipeline/47/wfapi/inputSubmit?inputId=3eaa25d43fac6e39a12c3936942b72c8"
        assert await async_pending_input.abort_url == "/job/input-pipeline/47/input/3eaa25d43fac6e39a12c3936942b72c8/abort"

    async def test_abort(self, async_pending_input, respx_mock):
        url = f'{async_pending_input.url}abort'
        respx_mock.post(url)
        await async_pending_input.abort()
        assert respx_mock.calls[0].request.url == url

    async def test_submit_empty(self, async_pending_input, respx_mock):
        url=f'{async_pending_input.url}proceedEmpty'
        respx_mock.post(url)
        await async_pending_input.submit()
        assert respx_mock.calls[0].request.url == url

    async def test_submit_arg(self, async_pending_input, respx_mock):
        async_pending_input.raw['inputs'] = [{'name': 'arg1'}]
        url = f'{async_pending_input.url}submit'
        respx_mock.post(url)
        await async_pending_input.submit(arg1='x')
        assert respx_mock.calls[0].request.url == url

    async def test_submit_empty_with_arg(self, async_pending_input):
        async_pending_input.raw['inputs'] = []
        with pytest.raises(TypeError):
            await async_pending_input.submit(arg1='x')

    async def test_submit_wrong_arg(self, async_pending_input):
        async_pending_input.raw['inputs'] = [{'name': 'arg1'}]
        with pytest.raises(TypeError):
            await async_pending_input.submit(arg2='x')