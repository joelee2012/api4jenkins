# encoding: utf-8

import pytest
from api4jenkins.credential import AsyncCredential, Credential


class TestCredentials:

    @pytest.mark.parametrize('id_, obj', [('not exist', type(None)), ('test-user', Credential)])
    def test_get(self, jenkins, id_, obj):
        assert isinstance(jenkins.credentials.get(id_), obj)

    def test_create(self, jenkins, respx_mock):
        req_url = f'{jenkins.credentials.url}createCredentials'
        respx_mock.post(req_url)
        jenkins.credentials.create('xml')
        assert respx_mock.calls[0].request.url == req_url

    def test_iter(self, jenkins):
        creds = list(jenkins.credentials)
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

    @pytest.mark.parametrize('id_, obj', [('not exist', type(None)), ('test-user', AsyncCredential)])
    async def test_get(self, async_jenkins, id_, obj):
        assert isinstance(await async_jenkins.credentials.get(id_), obj)

    async def test_create(self, async_jenkins, respx_mock):
        req_url = f'{async_jenkins.credentials.url}createCredentials'
        respx_mock.post(req_url)
        await async_jenkins.credentials.create('xml')
        assert respx_mock.calls[0].request.url == req_url

    async def test_iter(self, async_jenkins):
        creds = [c async for c in async_jenkins.credentials]
        assert len(creds) == 2
        assert all(isinstance(c, AsyncCredential) for c in creds)
