from .item import Item, camel, snake


class GetMixIn:

    def get(self, name):
        for item in self:
            if item.name == name:
                return item
        return None


class ResultBase:

    def __init__(self, raw):
        self.raw = raw

    def __getattr__(self, name):
        camel_name = camel(name)
        if camel_name in self.raw:
            return self.raw[camel_name]
        return super().__getattribute__(name)

    def __str__(self):
        return f'<{type(self).__name__}: {self.name}>'

    def __dir__(self):
        return super().__dir__() + [snake(k) for k in self.raw]


class TestReport(Item, GetMixIn):

    def __iter__(self):
        for suite in self.api_json()['suites']:
            yield TestSuite(suite)

    @property
    def suites(self):
        yield from self


class TestSuite(ResultBase, GetMixIn):

    def __iter__(self):
        for case in self.raw['cases']:
            yield TestCase(case)

    @property
    def cases(self):
        yield from self


class TestCase(ResultBase):
    pass
