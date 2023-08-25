import pytest
from api4jenkins.item import snake


class TestSystem:

    @pytest.mark.parametrize('action', ['restart', 'safeRestart', 'quietDown',
                                        'cancelQuietDown', 'exit', 'safeExit'])
    def test_enable_disable(self, jenkins, respx_mock, action):
        req_url = f'{jenkins.system.url}{action}'
        respx_mock.post(req_url)
        getattr(jenkins.system, snake(action))()
        assert respx_mock.calls[0].request.url == req_url


class TestAsyncSystem:

    @pytest.mark.parametrize('action', ['restart', 'safeRestart', 'quietDown',
                                        'cancelQuietDown', 'exit', 'safeExit'])
    async def test_enable_disable(self, async_jenkins, respx_mock, action):
        req_url = f'{async_jenkins.system.url}{action}'
        respx_mock.post(req_url)
        await getattr(async_jenkins.system, snake(action))()
        assert respx_mock.calls[0].request.url == req_url
