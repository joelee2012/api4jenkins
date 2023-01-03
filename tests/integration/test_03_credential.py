class TestGlobalCredential:
    def test_get(self, jenkins):
        c = jenkins.credentials.get('user-id')
        assert c.id == 'user-id'
        assert jenkins.credentials.get('not exists') is None


class TestFolderCredential:
    def test_get(self, folder):
        c = folder.credentials.get('user-id')
        assert c.id == 'user-id'
        assert folder.credentials.get('not exists') is None

    def test_iter(self, folder):
        assert len(list(folder.credentials)) == 1
