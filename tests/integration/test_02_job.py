# encoding: utf-8

import pytest


class TestFolder:

    def test_parent(self, jenkins, folder, job):
        assert folder == job.parent
        assert jenkins == folder.parent

    # @pytest.mark.xfail
    def test_credential(self, folder):
        c = folder.credentials.get('user-id')
        assert c.id == 'user-id'

    def test_iter_jobs(self, folder):
        assert len(list(folder.iter(2))) == 5
        assert len(list(folder(2))) == 5
        assert len(list(folder)) == 4
        assert folder['job']


class TestProject:
    def test_name(self, job):
        assert job.name == 'job'
        assert job.full_name == 'folder/job'
        assert job.full_display_name == 'folder » job'

    def test_get_parameters(self, args_job):
        assert args_job.get_parameters()[0]['name'] == 'ARG1'

    def test_get_build(self, job):
        assert job.get_build(0) is None
        assert job[1]

    def test_get_special_build(self, job):
        assert job.get_first_build()
        assert job.get_last_failed_build() is None

    def test_iter_build(self, job):
        assert len(list(job)) == 2
        assert len(list(job.iter_builds())) == 2

    def test_iter_all_builds(self, job):
        assert len(list(job.iter_all_builds())) == 2

    def test_building(self, job):
        assert job.building == False

    def test_set_next_build_number(self, job):
        job.set_next_build_number(10)
        assert job.next_build_number == 10

    def test_filter_builds_by_result(self, job):
        assert len(list(job.filter_builds_by_result(result='SUCCESS'))) == 2
        assert not list(job.filter_builds_by_result(result='ABORTED'))
        with pytest.raises(ValueError):
            assert list(job.filter_builds_by_result(
                result='not a status')) == 'x'
