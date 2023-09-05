# encoding: utf-8

import pytest

from api4jenkins.build import AsyncWorkflowRun, WorkflowRun
from api4jenkins.job import AsyncWorkflowJob, WorkflowJob
from api4jenkins.queue import AsyncQueueItem, QueueItem

from .conftest import load_json


class TestQueue:

    @pytest.mark.parametrize('id_, obj',
                             [(1, type(None)), (669, QueueItem)])
    def test_get(self, jenkins, id_, obj):
        assert isinstance(jenkins.queue.get(id_), obj)

    def test_iter(self, jenkins):
        items = list(jenkins.queue)
        assert len(items) == 2

    def test_cancel(self, jenkins, respx_mock):
        req_url = f'{jenkins.queue.url}cancelItem?id=0'
        respx_mock.post(req_url)
        jenkins.queue.cancel(0)
        assert respx_mock.calls[0].request.url == req_url


class TestQueueItem:

    @pytest.mark.parametrize('id_, type_',
                             [(669, 'blockeditem'),
                              (599, 'leftitem'),
                                 (700, 'waitingitem'),
                                 (668, 'buildableitem')])
    def test_get_job(self, jenkins, job, id_, type_, monkeypatch):
        item = QueueItem(jenkins, f'{jenkins.url}queue/item/{id_}/')

        def _api_json(tree='', depth=0):
            return load_json(f'queue/{type_}.json')

        monkeypatch.setattr(item, 'api_json', _api_json)
        assert job == item.get_job()

    @pytest.mark.parametrize('id_, type_, obj',
                             [(669, 'blockeditem', type(None)),
                              (599, 'leftitem', WorkflowRun),
                                 (668, 'waitingitem', WorkflowRun),
                                 (668, 'buildableitem', WorkflowRun)])
    def test_get_build(self, jenkins, id_, type_, obj, monkeypatch):
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


class TestAsyncQueue:

    @pytest.mark.parametrize('id_, obj',
                             [(1, type(None)), (669, AsyncQueueItem)])
    async def test_get(self, async_jenkins, id_, obj):
        assert isinstance(await async_jenkins.queue.get(id_), obj)

    async def test_iter(self, async_jenkins):
        items = [i async for i in async_jenkins.queue]
        assert len(items) == 2

    async def test_cancel(self, async_jenkins, respx_mock):
        req_url = f'{async_jenkins.queue.url}cancelItem?id=0'
        respx_mock.post(req_url)
        await async_jenkins.queue.cancel(0)
        assert respx_mock.calls[0].request.url == req_url


class TestAsyncQueueItem:

    @pytest.mark.parametrize('id_, type_',
                             [(669, 'blockeditem'),
                              (599, 'leftitem'),
                                 (700, 'waitingitem'),
                                 (668, 'buildableitem')])
    async def test_get_job(self, async_jenkins, async_job, id_, type_, monkeypatch):
        item = AsyncQueueItem(
            async_jenkins, f'{async_jenkins.url}queue/item/{id_}/')

        async def _api_json(tree='', depth=0):
            return load_json(f'queue/{type_}.json')

        monkeypatch.setattr(item, 'api_json', _api_json)
        job = await item.get_job()
        assert isinstance(job, AsyncWorkflowJob)
        assert job == job

    @pytest.mark.parametrize('id_, type_, obj',
                             [(669, 'blockeditem', type(None)),
                              (599, 'leftitem', AsyncWorkflowRun),
                                 (668, 'waitingitem', AsyncWorkflowRun),
                                 (668, 'buildableitem', AsyncWorkflowRun)])
    async def test_get_build(self, async_jenkins, id_, type_, obj, monkeypatch):
        item = AsyncQueueItem(
            async_jenkins, f'{async_jenkins.url}queue/item/{id_}/')

        async def _api_json(tree='', depth=0):
            return load_json(f'queue/{type_}.json')

        monkeypatch.setattr(item, 'api_json', _api_json)
        assert isinstance(await item.get_build(), obj)

    async def test_get_parameters(self, async_jenkins):
        item = AsyncQueueItem(
            async_jenkins, f'{async_jenkins.url}queue/item/668/')
        params = await item.get_parameters()
        assert len(params) == 0

    async def test_get_causes(self, async_jenkins):
        item = AsyncQueueItem(
            async_jenkins, f'{async_jenkins.url}queue/item/668/')
        causes = await item.get_causes()
        assert causes[0]['shortDescription'] == 'Triggered by'
