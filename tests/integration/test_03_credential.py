class TestCredentials:
    def test_credentials_iter(self, jenkins):
        assert len(list(jenkins.credentials)) == 2

    def test_credential_get(self, jenkins):
        assert jenkins.credentials.global_domain is not None
        assert jenkins.credentials.get('not exists') is None

    def test_domain_get(self, jenkins):
        c = jenkins.credentials.global_domain['user-id']
        assert c.id == 'user-id'
        assert jenkins.credentials.global_domain['not exists'] is None

    def test_domain_iter(self, folder):
        assert len(list(folder.credentials.global_domain)) == 1


class TestAsyncCredential:
    async def test_credentials_iter(self, async_jenkins):
        assert len([c async for c in async_jenkins.credentials]) == 2

    async def test_credential_get(self, async_jenkins):
        domain = await async_jenkins.credentials.global_domain
        assert domain is not None
        domain = await async_jenkins.credentials.get('not exists')
        assert domain is None

    async def test_domain_get(self, async_jenkins):
        domain = await async_jenkins.credentials.global_domain
        c = await domain['user-id']
        assert await c.id == 'user-id'
        c = await domain['not exists']
        assert c is None

    async def test_domain_iter(self, async_folder):
        assert len([c async for c in await async_folder.credentials.global_domain]) == 1
