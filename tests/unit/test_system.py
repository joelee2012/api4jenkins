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

    def test_reload_jcasc(self, jenkins, respx_mock):
        req_url = f'{jenkins.system.url}configuration-as-code/reload'
        respx_mock.post(req_url)
        jenkins.system.reload_jcasc()
        assert respx_mock.calls[0].request.url == req_url

    def test_export_jcasc(self, jenkins, respx_mock):
        req_url = f'{jenkins.system.url}configuration-as-code/export'
        respx_mock.post(req_url)
        jenkins.system.export_jcasc()
        assert respx_mock.calls[0].request.url == req_url

    def test_apply_jcasc(self, jenkins, respx_mock):
        check_url = f'{jenkins.system.url}configuration-as-code/checkNewSource?newSource=yaml'
        respx_mock.post(check_url)
        req_url = f'{jenkins.system.url}configuration-as-code/replace'
        respx_mock.post(req_url)
        jenkins.system.apply_jcasc('yaml')
        assert respx_mock.calls[0].request.url == check_url
        assert respx_mock.calls[1].request.url == req_url

    def test_apply_jcasc_fail(self, jenkins, respx_mock):
        check_url = f'{jenkins.system.url}configuration-as-code/checkNewSource?newSource=yaml'
        respx_mock.post(check_url).respond(text='<div class=error>')
        with pytest.raises(ValueError):
            jenkins.system.apply_jcasc('yaml')
        assert respx_mock.calls[0].request.url == check_url


class TestAsyncSystem:

    @pytest.mark.parametrize('action', ['restart', 'safeRestart', 'quietDown',
                                        'cancelQuietDown', 'exit', 'safeExit'])
    async def test_enable_disable(self, async_jenkins, respx_mock, action):
        req_url = f'{async_jenkins.system.url}{action}'
        respx_mock.post(req_url)
        await getattr(async_jenkins.system, snake(action))()
        assert respx_mock.calls[0].request.url == req_url

    async def test_reload_jcasc(self, async_jenkins, respx_mock):
        req_url = f'{async_jenkins.system.url}configuration-as-code/reload'
        respx_mock.post(req_url)
        await async_jenkins.system.reload_jcasc()
        assert respx_mock.calls[0].request.url == req_url

    async def test_export_jcasc(self, async_jenkins, respx_mock):
        req_url = f'{async_jenkins.system.url}configuration-as-code/export'
        respx_mock.post(req_url)
        await async_jenkins.system.export_jcasc()
        assert respx_mock.calls[0].request.url == req_url

    async def test_apply_jcasc(self, async_jenkins, respx_mock):
        check_url = f'{async_jenkins.system.url}configuration-as-code/checkNewSource?newSource=yaml'
        respx_mock.post(check_url)
        req_url = f'{async_jenkins.system.url}configuration-as-code/replace'
        respx_mock.post(req_url)
        await async_jenkins.system.apply_jcasc('yaml')
        assert respx_mock.calls[0].request.url == check_url
        assert respx_mock.calls[1].request.url == req_url

    async def test_apply_jcasc_fail(self, async_jenkins, respx_mock):
        check_url = f'{async_jenkins.system.url}configuration-as-code/checkNewSource?newSource=yaml'
        respx_mock.post(check_url).respond(text='<div class=error>')
        with pytest.raises(ValueError):
            await async_jenkins.system.apply_jcasc('yaml')
        assert respx_mock.calls[0].request.url == check_url
