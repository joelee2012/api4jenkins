import pytest


@pytest.fixture
def suite(workflowrun):
    return workflowrun.get_test_report().get('pytest')


@pytest.fixture
def case(suite):
    return suite.get('test_exists')


@pytest.fixture
def coverage_report(workflowrun):
    return workflowrun.get_coverage_report()


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

    def test_get(self, workflowrun):
        cr = workflowrun.get_coverage_result()
        assert cr.get('Report').ratio == 100
        assert cr.get('Line').ratio == 83.83372
