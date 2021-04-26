# encoding: utf-8

import pytest
from api4jenkins.build import WorkflowRun
from api4jenkins.job import WorkflowJob
from api4jenkins.queue import QueueItem

from .conftest import load_json


class TestQueue:

    @pytest.mark.parametrize('id_, obj',
                             [(1, type(None)), (669, QueueItem)])
    def test_get(self, jenkins, id_, obj):
        assert isinstance(jenkins.queue.get(id_), obj)

    def test_iter(self, jenkins):
        items = list(jenkins.queue)
        assert len(items) == 2


class TestQueueItem:

    @pytest.mark.parametrize('id_, type_',
                             [(669, 'blockeditem'),
                              (599, 'leftitem'),
                                 (700, 'waitingitem'),
                                 (668, 'buildableitem')])
    def test_get_job(self, jenkins, workflow, id_, type_, monkeypatch):
        item = QueueItem(jenkins, f'{jenkins.url}queue/item/{id_}/')

        def _api_json(tree='', depth=0):
            return load_json(f'queue/{type_}.json')

        monkeypatch.setattr(item, 'api_json', _api_json)
        job = item.get_job()
        assert isinstance(job, WorkflowJob)
        assert job == workflow

    @pytest.mark.parametrize('id_, type_, obj',
                             [(669, 'blockeditem', type(None)),
                              (599, 'leftitem', WorkflowRun),
                                 (668, 'waitingitem', WorkflowRun),
                                 (668, 'buildableitem', WorkflowRun)])
    def test_get_build(self, jenkins, workflowrun, id_, type_, obj, monkeypatch):
        item = QueueItem(jenkins, f'{jenkins.url}queue/item/{id_}/')

        def _api_json(tree='', depth=0):
            return load_json(f'queue/{type_}.json')

        monkeypatch.setattr(item, 'api_json', _api_json)
        build = item.get_build()
        assert isinstance(build, obj)

    def test_get_parameters(self, jenkins):
        item = QueueItem(jenkins, f'{jenkins.url}queue/item/668/')
        params = item.get_parameters()
        assert len(params) == 0

    def test_get_causes(self, jenkins):
        item = QueueItem(jenkins, f'{jenkins.url}queue/item/668/')
        causes = item.get_causes()
        assert causes[0]['shortDescription'] == 'Triggered by'
