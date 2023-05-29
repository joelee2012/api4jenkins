class TestGlobalView:
    def test_get(self, jenkins):
        v = jenkins.views.get('global-view')
        assert v.name == 'global-view'
        assert jenkins.views.get('not exist') is None

    def test_iter(self, jenkins):
        assert len(list(jenkins.views)) == 2

    def test_in_exclude(self, jenkins):
        v = jenkins.views.get('global-view')
        assert v['folder'] is None
        v.include('folder')
        assert v['folder']
        v.exclude('folder')
        assert v['folder'] is None


class TestFolderView:
    def test_get(self, folder):
        v = folder.views.get('folder-view')
        assert v.name == 'folder-view'
        assert folder.views.get('not exist') is None
