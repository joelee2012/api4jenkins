import pytest
from api4jenkins.artifact import Artifact


@pytest.fixture
def artifact(jenkins):
    raw = {
        "id": "n3",
        "name": "hello2.jar",
        "path": "target/hello2.jar",
        "url": "/job/test/1/artifact/target/hello2.jar",
        "size": 6
    }
    return Artifact(jenkins, raw)


class TestArtifact:

    def test_attrs(self, artifact, jenkins):
        assert artifact.id == "n3"
        assert artifact.name == "hello2.jar"
        assert artifact.path == "target/hello2.jar"
        assert artifact.url == f'{jenkins.url}job/test/1/artifact/target/hello2.jar'
        assert artifact.size == 6

    def test_save(self, artifact, mock_resp, tmp_path):
        mock_resp.add('GET', artifact.url, body='abcd')
        filename = tmp_path / artifact.name
        artifact.save(filename)
        assert filename.exists()
