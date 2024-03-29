# encoding: utf-8
from .item import AsyncItem, Item, camel, snake


class GetMixIn:

    def get(self, name):
        return next((item for item in self if item.name == name), None)


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


class CoverageReport(Item, GetMixIn):
    '''Access coverage report generated by `JaCoCo <https://plugins.jenkins.io/jacoco/>`_'''

    report_types = ['branchCoverage', 'classCoverage', 'complexityScore',
                    'instructionCoverage', 'lineCoverage', 'methodCoverage']

    def __getattr__(self, name):
        attr = camel(name)
        if attr not in self.report_types:
            raise AttributeError(
                f"'CoverageReport' object has no attribute '{name}'")
        return self.get(attr)

    def __iter__(self):
        for k, v in self.api_json().items():
            if k not in ['_class', 'previousResult']:
                v['name'] = k
                yield Coverage(v)

    def trends(self, count=2):
        def _resolve(data):
            if data['previousResult']:
                yield from _resolve(data['previousResult'])
            for k, v in data.items():
                if k not in ['_class', 'previousResult']:
                    v['name'] = k
                    yield Coverage(v)

        yield from _resolve(self.api_json(depth=count))


class Coverage(ResultBase):
    pass


class CoverageResult(Item, GetMixIn):
    '''Access coverage result generated by `Code Coverage API <https://plugins.jenkins.io/code-coverage-api/>`_'''

    def __iter__(self):
        for element in self.api_json(depth=1)['results']['elements']:
            yield CoverageElement(element)


class CoverageElement(ResultBase):
    pass


class CoverageTrends(Item, GetMixIn):
    def __iter__(self):
        for trend in self.api_json(depth=1)['trends']:
            trend['name'] = trend['buildName']
            yield CoverageTrend(trend)


class CoverageTrend(ResultBase):

    def __iter__(self):
        for element in self.raw['elements']:
            yield CoverageElement(element)


# async class

class AsyncGetMixIn:

    async def get(self, name):
        async for item in self:
            if item.name == name:
                return item


class AsyncTestReport(AsyncItem, AsyncGetMixIn):

    async def __aiter__(self):
        data = await self.api_json()
        for suite in data['suites']:
            yield TestSuite(suite)

    @property
    async def suites(self):
        async for suite in self:
            yield suite


class AsyncCoverageReport(AsyncItem, AsyncGetMixIn):
    '''Access coverage report generated by `JaCoCo <https://plugins.jenkins.io/jacoco/>`_'''

    report_types = ['branchCoverage', 'classCoverage', 'complexityScore',
                    'instructionCoverage', 'lineCoverage', 'methodCoverage']

    async def __getattr__(self, name):
        attr = camel(name)
        if attr not in self.report_types:
            raise AttributeError(
                f"'CoverageReport' object has no attribute '{name}'")
        return await self.get(attr)

    async def __aiter__(self):
        data = await self.api_json()
        for k, v in data.items():
            if k not in ['_class', 'previousResult']:
                v['name'] = k
                yield Coverage(v)

    async def trends(self, count=2):
        def _resolve(data):
            if data['previousResult']:
                yield from _resolve(data['previousResult'])
            for k, v in data.items():
                if k not in ['_class', 'previousResult']:
                    v['name'] = k
                    yield Coverage(v)
        data = await self.api_json(depth=count)
        for c in _resolve(data):
            yield c


class AsyncCoverageResult(AsyncItem, AsyncGetMixIn):
    '''Access coverage result generated by `Code Coverage API <https://plugins.jenkins.io/code-coverage-api/>`_'''

    async def __aiter__(self):
        data = await self.api_json(depth=1)
        for element in data['results']['elements']:
            yield CoverageElement(element)


class AsyncCoverageTrends(AsyncItem, AsyncGetMixIn):
    async def __aiter__(self):
        data = await self.api_json(depth=1)
        for trend in data['trends']:
            trend['name'] = trend['buildName']
            yield CoverageTrend(trend)
