
import pytest


@pytest.fixture
def node(jenkins):
    return jenkins.nodes.get('Built-In Node')


@pytest.fixture
async def anode(async_jenkins):
    return await async_jenkins.nodes.get('Built-In Node')


class TestNode:
    def test_get(self, node):
        assert node.display_name == 'Built-In Node'

    def test_iter(self, jenkins):
        assert len(list(jenkins.nodes)) == 1

    def test_filter_node_by_label(self, jenkins):
        assert len(list(jenkins.nodes.filter_node_by_label('built-in'))) == 1

    def test_filter_node_by_status(self, jenkins):
        assert len(list(jenkins.nodes.filter_node_by_status(online=True))) == 1

    def test_enable_disable(self, node):
        assert node.offline == False
        node.disable()
        assert node.offline
        node.enable()

    def test_iter_build_on_node(self, node):
        assert not list(node)


class TestAsyncNode:
    async def test_get(self, anode):
        assert await anode.display_name == 'Built-In Node'

    async def test_iter(self, async_jenkins):
        assert len([n async for n in async_jenkins.nodes]) == 1

    async def test_filter_node_by_label(self, async_jenkins):
        assert len([n async for n in async_jenkins.nodes.filter_node_by_label('built-in')]) == 1

    async def test_filter_node_by_status(self, async_jenkins):
        assert len([n async for n in async_jenkins.nodes.filter_node_by_status(online=True)]) == 1

    async def test_enable_disable(self, anode):
        assert await anode.offline == False
        await anode.disable()
        assert await anode.offline
        await anode.enable()

    async def test_iter_build_on_node(self, anode):
        assert not [b async for b in anode]
