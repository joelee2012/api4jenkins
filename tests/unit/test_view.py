# encoding: utf-8
import pytest
from api4jenkins.view import AllView, AsyncAllView


class TestViews:

    def test_get(self, jenkins):
        view = jenkins.views.get('all')
        assert isinstance(view, AllView)
        assert view.url == jenkins.url + 'view/all/'
        assert jenkins.views.get('not exist') is None

    def test_views(self, jenkins):
        assert len(list(jenkins.views)) == 1


class TestView:

    def test_get_job(self, view):
        job_in_view = view['folder']
        job = view.jenkins.get_job('folder')
        assert job_in_view == job
        assert view['not exist'] is None

    def test_iter(self, view):
        assert len(list(view)) == 2

    @pytest.mark.parametrize('action, entry', [('include', 'addJobToView'),
                                               ('exclude', 'removeJobFromView')])
    def test_include_exclude(self, view, respx_mock, action, entry):
        req_url = f'{view.url}{entry}?name=folder1'
        respx_mock.post(req_url).respond(json={'name': 'folder1'})
        getattr(view, action)('folder1')
        assert respx_mock.calls[0].request.url == req_url


class TestAsyncViews:

    async def test_get(self, async_jenkins):
        view = await async_jenkins.views['all']
        assert isinstance(view, AsyncAllView)
        assert view.url == f'{async_jenkins.url}view/all/'
        assert await async_jenkins.views['not exist'] is None

    async def test_views(self, async_jenkins):
        assert len([view async for view in async_jenkins.views]) == 1


class TestAsyncView:

    async def test_get_job(self, async_view, async_folder):
        job_in_view = await async_view['folder']
        assert job_in_view == async_folder
        assert await async_view['not exist'] is None

    async def test_iter(self, async_view):
        assert len([job async for job in async_view]) == 2

    @pytest.mark.parametrize('action, entry', [('include', 'addJobToView'),
                                               ('exclude', 'removeJobFromView')])
    async def test_include_exclude(self, async_view, respx_mock, action, entry):
        req_url = f'{async_view.url}{entry}?name=folder1'
        respx_mock.post(req_url).respond(json={'name': 'folder1'})
        await getattr(async_view, action)('folder1')
        assert respx_mock.calls[0].request.url == req_url
