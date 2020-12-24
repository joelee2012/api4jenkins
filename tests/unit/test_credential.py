# encoding: utf-8

import pytest
from api4jenkins.credential import Credential


class TestCredentials:

    @pytest.mark.parametrize('id_, obj', [('not exist', type(None)), ('test-user', Credential)])
    def test_get(self, jenkins, id_, obj):
        assert isinstance(jenkins.credentials.get(id_), obj)

    def test_create(self, jenkins, mock_resp):
        req_url = f'{jenkins.credentials.url}createCredentials'
        mock_resp.add('POST', req_url)
        jenkins.credentials.create('xml')
        assert mock_resp.calls[0].request.url == req_url

    def test_iter(self, jenkins):
        creds = list(jenkins.credentials)
        assert len(creds) == 2
        assert all([isinstance(c, Credential) for c in creds])


class TestCredential:

    def test_delete(self, credential, mock_resp):
        req_url = f'{credential.url}doDelete'
        mock_resp.add('POST', req_url)
        credential.delete()
        assert mock_resp.calls[0].response.status_code == 200
        assert mock_resp.calls[0].request.url == req_url

    @pytest.mark.parametrize('req, xml, body',
                             [('GET', None, '<xml/>'), ('POST', '<xml/>', '')],
                             ids=['get', 'set'])
    def test_configure(self, credential, mock_resp, req, xml, body):
        req_url = f'{credential.url}config.xml'
        mock_resp.add(req, req_url, body=body)
        text = credential.configure(xml)
        assert mock_resp.calls[0].request.url == req_url
        if req == 'GET':
            assert text == body
