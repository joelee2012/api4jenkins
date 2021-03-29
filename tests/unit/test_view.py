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
        job_in_view = view.get_job('Level1_Folder1')
        job = view.jenkins.get_job('Level1_Folder1')
        assert job_in_view == job
        assert view.get_job('not exist') is None

    def test_iter(self, view):
        assert len(list(view)) == 2

    @pytest.mark.parametrize('action, entry', [('include', 'addJobToView'),
                                               ('exclude', 'removeJobFromView')])
    def test_include_exclude(self, view, mock_resp, action, entry):
        req_url = f'{view.url}{entry}?name=folder1'
        mock_resp.add('POST', req_url, json={'name': 'folder1'})
        getattr(view, action)('folder1')
        assert mock_resp.calls[0].request.url == req_url
