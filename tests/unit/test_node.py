# encoding: utf-8


class TestNodes:

    def test_get(self, jenkins):
        node = jenkins.nodes.get('master')
        assert node.display_name == 'master'
        assert jenkins.nodes.get('notexist') is None

    def test_iter(self, jenkins):
        nodes = list(jenkins.nodes)
        assert len(nodes) == 2
        assert nodes[0].display_name == 'master'

    def test_iter_builds(self, jenkins):
        builds = list(jenkins.nodes.iter_builds())
        assert len(builds) == 2
        assert builds[0].url == 'http://0.0.0.0:8080/job/Level1_freestylejob/14/'
        assert builds[1].url == 'http://0.0.0.0:8080/job/Level1_WorkflowJob1/54/'


class TestNode:

    def test_iter_builds(self, jenkins):
        node = jenkins.nodes.get('master')
        builds = list(node)
        assert len(builds) == 2
        assert builds[0].url == 'http://0.0.0.0:8080/job/Level1_freestylejob/14/'
        assert builds[1].url == 'http://0.0.0.0:8080/job/Level1_WorkflowJob1/54/'
