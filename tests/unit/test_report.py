import pytest


@pytest.fixture
def suite(build):
    return build.get_test_report().get('pytest')


@pytest.fixture
def case(suite):
    return suite.get('test_exists')


@pytest.fixture
def coverage_report(build):
    return build.get_coverage_report()


class TestTestReport:

    def test_attributes(self, test_report):
        assert test_report.fail_count == 2
        assert test_report.pass_count == 37

    def test_iterate(self, test_report):
        assert len(list(test_report)) == 1
        assert len(list(test_report.suites)) == 1


class TestTestSuite:

    def test_attributes(self, suite):
        assert suite.name == 'pytest'
        assert suite.duration == 74.678

    def test_get_case(self, suite):
        case = suite.get('test_exists')
        assert case.name == 'test_exists'
        assert case.status == 'PASSED'
        assert suite.get('notexist') is None

    def test_iterate(self, suite):
        assert len(list(suite)) == 1
        assert len(list(suite.cases)) == 1


class TestTestCase:

    def test_attributes(self, case):
        assert case.name == 'test_exists'
        assert case.status == 'PASSED'


class TestCoverageReport:

    def test_attributes(self, coverage_report):
        assert coverage_report.branch_coverage.covered == 244
        assert coverage_report.method_coverage.covered == 320

    def test_get(self, coverage_report):
        assert coverage_report.get('branchCoverage').covered == 244
        assert coverage_report.get('methodCoverage').covered == 320

    def test_wrong_attribute(self, coverage_report):
        with pytest.raises(AttributeError):
            coverage_report.xxxxx


class TestCoverageResult:

    def test_get(self, build):
        cr = build.get_coverage_result()
        assert cr.get('Report').ratio == 100
        assert cr.get('Line').ratio == 83.83372


@pytest.fixture
async def async_suite(async_test_report):
    return await async_test_report.get('pytest')


@pytest.fixture
async def async_case(async_suite):
    return await async_suite.get('test_exists')


@pytest.fixture
async def async_coverage_report(async_build):
    return await async_build.get_coverage_report()


@pytest.fixture
async def async_test_report(async_build):
    return await async_build.get_test_report()


class TestAsyncTestReport:

    async def test_attributes(self, async_test_report):
        assert await async_test_report.fail_count == 2
        assert await async_test_report.pass_count == 37

    async def test_iterate(self, async_test_report):
        assert len([s async for s in async_test_report]) == 1
        assert len([s async for s in async_test_report.suites]) == 1


class TestAsyncCoverageReport:

    async def test_attributes(self, async_coverage_report):
        assert (await async_coverage_report.branch_coverage).covered == 244
        assert (await async_coverage_report.method_coverage).covered == 320

    async def test_get(self, async_coverage_report):
        assert (await async_coverage_report.get('branchCoverage')).covered == 244
        assert (await async_coverage_report.get('methodCoverage')).covered == 320

    async def test_wrong_attribute(self, async_coverage_report):
        with pytest.raises(AttributeError):
            await async_coverage_report.xxxxx
