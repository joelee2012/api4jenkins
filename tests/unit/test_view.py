# encoding: utf-8
import pytest
from api4jenkins.view import AllView


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
        job_in_view = view.get_job('folder')
        job = view.jenkins.get_job('folder')
        assert job_in_view == job
        assert view.get_job('not exist') is None

    def test_iter(self, view):
        assert len(list(view)) == 2

    @pytest.mark.parametrize('action, entry', [('include', 'addJobToView'),
                                               ('exclude', 'removeJobFromView')])
    def test_include_exclude(self, view, respx_mock, action, entry):
        req_url = f'{view.url}{entry}?name=folder1'
        respx_mock.post(req_url).respond(json={'name': 'folder1'})
        getattr(view, action)('folder1')
        assert respx_mock.calls[0].request.url == req_url
