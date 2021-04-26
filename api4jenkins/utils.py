from .job import Project
from .node import Node


def filter_node_by_label(nodes, *labels):
    for node in nodes:
        for label in node.api_json()['assignedLabels']:
            if label['name'] in labels:
                yield node


def filter_node_by_status(nodes, *, online):
    yield from filter(lambda node: online != node.offline, nodes)


def filter_building_builds(node):
    if not isinstance(node, (Node, Project)):
        raise ValueError('Must be Node or Project')
    yield from filter(lambda build: build.building, node)


def filter_building_builds_on_nodes(nodes):
    for node in nodes:
        yield from filter_building_builds(node)


def filter_build_by_result(job, *, result):
    """filter build by build results, avaliable results are:
    'SUCCESS', 'UNSTABLE', 'FAILURE', 'NOT_BUILT', 'ABORTED'
    see: https://javadoc.jenkins-ci.org/hudson/model/Result.html
    """
    expect = ['SUCCESS', 'UNSTABLE', 'FAILURE', 'NOT_BUILT', 'ABORTED']
    if result not in expect:
        raise ValueError(f'Expect one of {expect}')
    yield from filter(lambda build: build.result == result, job)
