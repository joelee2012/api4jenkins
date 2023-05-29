# encoding: utf-8

import pytest
from api4jenkins.credential import Credential


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
        assert all([isinstance(c, Credential) for c in creds])


class TestCredential:

    def test_delete(self, new_credential, respx_mock):
        req_url = f'{new_credential.url}doDelete'
        respx_mock.post(req_url)
        new_credential.delete()
        assert respx_mock.calls[0].response.status_code == 200
        assert respx_mock.calls[0].request.url == req_url

    @pytest.mark.parametrize('req, xml, body',
                             [('GET', None, '<xml/>'), ('POST', '<xml/>', '')],
                             ids=['get', 'set'])
    def test_configure(self, new_credential, respx_mock, req, xml, body):
        req_url = f'{new_credential.url}config.xml'
        respx_mock.route(method=req, url=req_url).respond(content=body)
        text = new_credential.configure(xml)
        assert respx_mock.calls[0].request.url == req_url
        if req == 'GET':
            assert text == body
