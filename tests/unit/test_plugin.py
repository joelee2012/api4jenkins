# encoding: utf-8

import pytest
from api4jenkins.plugin import Plugin


class TestPlugins:

    @pytest.mark.parametrize('name, obj',
                             [('not exist', type(None)), ('git', Plugin)])
    def test_get(self, jenkins, name, obj):
        assert isinstance(jenkins.plugins.get(name), obj)
