import pytest
from api4jenkins.item import snake


class TestSystem:

    @pytest.mark.parametrize('action', ['restart', 'safeRestart', 'quietDown',
                                        'cancelQuietDown', 'exit', 'safeExit'])
    def test_enable_disable(self, jenkins, mock_resp, action):
        req_url = f'{jenkins.system.url}{action}'
        mock_resp.add('POST', req_url)
        getattr(jenkins.system, snake(action))()
        assert mock_resp.calls[0].request.url == req_url
