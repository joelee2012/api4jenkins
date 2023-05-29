import pytest
import yaml

conf = '''unclassified:
  timestamper:
    allPipelines: true
'''


class TestSystem:
    def test_export_jcasc(self, jenkins):
        data = yaml.safe_load(jenkins.system.export_jcasc())
        assert data['unclassified']['timestamper']['allPipelines'] == False

    @pytest.mark.xfail
    def test_apply_jcasc(self, jenkins):
        jenkins.system.apply_jcasc(conf)
        # jenkins.system.reload_jcasc()
        data = yaml.safe_load(jenkins.system.export_jcasc())
        assert data['unclassified']['timestamper']['allPipelines']


class TestAsyncSystem:
    async def test_export_jcasc(self, async_jenkins):
        data = yaml.safe_load(await async_jenkins.system.export_jcasc())
        assert data['unclassified']['timestamper']['allPipelines'] == False

    @pytest.mark.xfail
    async def test_apply_jcasc(self, async_jenkins):
        await async_jenkins.system.apply_jcasc(conf)
        await async_jenkins.system.reload_jcasc()
        data = yaml.safe_load(await async_jenkins.system.export_jcasc())
        assert data['unclassified']['timestamper']['allPipelines']
