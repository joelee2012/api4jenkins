class TestCredentials:
    def test_credentials_iter(self, folder):
        assert len(list(folder.credentials)) == 2

    def test_credential_get(self, folder):
        assert folder.credentials.global_domain is not None
        assert folder.credentials.get('not exists') is None

    def test_domain_get(self, folder):
        c = folder.credentials.global_domain['user-id']
        assert c.id == 'user-id'
        assert folder.credentials.global_domain['not exists'] is None

    def test_domain_iter(self, folder):
        assert len(list(folder.credentials.global_domain)) == 1