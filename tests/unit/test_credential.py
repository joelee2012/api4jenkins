# encoding: utf-8

import pytest
from api4jenkins.credential import AsyncCredential, AsyncDomain, Credential, Domain


@pytest.fixture
def global_domain(jenkins):
    return jenkins.credentials.global_domain


@pytest.fixture
async def async_global_domain(async_jenkins):
    return await async_jenkins.credentials.global_domain


class TestCredentials:

    def test_get(self, jenkins):
        assert isinstance(jenkins.credentials['_'], Domain)
        assert jenkins.credentials['x'] is None

    def test_create(self, jenkins, respx_mock):
        req_url = f'{jenkins.credentials.url}createDomain'
        respx_mock.post(req_url)
        jenkins.credentials.create('xml')
        assert respx_mock.calls[0].request.url == req_url

    def test_iter(self, jenkins):
        assert len(list(jenkins.credentials)) == 3


class TestDomain:

    @pytest.mark.parametrize('id_, obj', [('not exist', type(None)), ('test-user', Credential)])
    def test_get(self, global_domain, id_, obj):
        assert isinstance(global_domain[id_], obj)

    def test_create(self, global_domain, respx_mock):
        req_url = f'{global_domain.url}createCredentials'
        respx_mock.post(req_url)
        global_domain.create('xml')
        assert respx_mock.calls[0].request.url == req_url

    def test_iter(self, global_domain):
        creds = list(global_domain)
        assert len(creds) == 2
        assert all(isinstance(c, Credential) for c in creds)


class TestCredential:

    def test_delete(self, credential, respx_mock):
        req_url = f'{credential.url}doDelete'
        respx_mock.post(req_url)
        credential.delete()
        assert respx_mock.calls[0].response.status_code == 200
        assert respx_mock.calls[0].request.url == req_url

    @pytest.mark.parametrize('req, xml, body',
                             [('GET', None, '<xml/>'), ('POST', '<xml/>', '')],
                             ids=['get', 'set'])
    def test_configure(self, credential, respx_mock, req, xml, body):
        req_url = f'{credential.url}config.xml'
        respx_mock.route(method=req, url=req_url).respond(content=body)
        text = credential.configure(xml)
        assert respx_mock.calls[0].request.url == req_url


class TestAsyncCredentials:

    async def test_get(self, async_jenkins):
        assert isinstance(await async_jenkins.credentials['_'], AsyncDomain)
        assert await async_jenkins.credentials['x'] is None

    async def test_create(self, async_jenkins, respx_mock):
        req_url = f'{async_jenkins.credentials.url}createDomain'
        respx_mock.post(req_url)
        await async_jenkins.credentials.create('xml')
        assert respx_mock.calls[0].request.url == req_url

    async def test_iter(self, async_jenkins):
        assert len([c async for c in async_jenkins.credentials]) == 3


class TestAsyncDomain:

    @pytest.mark.parametrize('id_, obj', [('not exist', type(None)), ('test-user', AsyncCredential)])
    async def test_get(self, async_global_domain, id_, obj):
        assert isinstance(await async_global_domain[id_], obj)

    async def test_create(self, async_global_domain, respx_mock):
        req_url = f'{async_global_domain.url}createCredentials'
        respx_mock.post(req_url)
        await async_global_domain.create('xml')
        assert respx_mock.calls[0].request.url == req_url

    async def test_iter(self, async_global_domain):
        creds = [c async for c in async_global_domain]
        assert len(creds) == 2
        assert all(isinstance(c, AsyncCredential) for c in creds)
