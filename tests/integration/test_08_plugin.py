import pytest


@pytest.fixture
def plugin(jenkins):
    jenkins.plugins.install('nodejs', block=True)
    yield jenkins.plugins.get('nodejs')
    jenkins.plugins.uninstall('nodejs')


@pytest.fixture
async def async_plugin(async_jenkins):
    await async_jenkins.plugins.install('nodejs', block=True)
    yield await async_jenkins.plugins.get('nodejs')
    await async_jenkins.plugins.uninstall('nodejs')


class TestPlugin:
    def test_get(self, jenkins):
        assert jenkins.plugins.get('git')
        assert jenkins.plugins.get('notxist') is None

    def test_install(self, plugin):
        assert plugin.short_name == 'nodejs'


class TestAsyncPlugin:
    async def test_get(self, async_jenkins):
        assert await async_jenkins.plugins.get('git')
        assert await async_jenkins.plugins.get('notxist') is None

    async def test_install(self, async_plugin):
        assert await async_plugin.short_name == 'nodejs'
