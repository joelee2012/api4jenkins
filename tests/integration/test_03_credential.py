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


class TestAsyncFolderCredential:
    async def test_get(self, async_folder):
        c = await async_folder.credentials.get('user-id')
        assert await c.id == 'user-id'
        assert await async_folder.credentials.get('not exists') is None

    async def test_iter(self, async_folder):
        assert len([c async for c in async_folder.credentials]) == 1
