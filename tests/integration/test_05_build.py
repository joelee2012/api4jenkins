# encoding: utf-8


class TestBuild:
    def test_get_job(self, job):
        assert job == job[1].job

    def test_console_text(self, job):
        assert 'true' in ''.join(job[1].console_text())

    def test_get_next_build(self, job):
        assert job[1].get_next_build().number == 2
        assert job[2].get_next_build() is None

    def test_get_previous_build(self, job):
        assert job[2].get_previous_build().number == 1
        assert job[1].get_previous_build() is None

    def test_coverage_report(self, job):
        pass
