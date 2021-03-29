import pytest


@pytest.fixture
def suite(test_report):
    return test_report.get('pytest')


@pytest.fixture
def case(suite):
    return suite.get('test_exists')


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
