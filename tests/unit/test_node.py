# encoding: utf-8


class TestNodes:

    def test_get(self, jenkins):
        node = jenkins.nodes.get('master')
        assert node.display_name == 'master'
