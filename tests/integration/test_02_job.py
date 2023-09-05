# encoding: utf-8

import pytest


class TestFolder:

    def test_parent(self, jenkins, folder, job):
        assert folder == job.parent
        assert jenkins == folder.parent

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
        assert job[0] is None
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


class TestAsyncFolder:
    async def test_parent(self, async_jenkins, async_folder, async_job):
        assert async_folder == await async_job.parent
        assert async_jenkins == await async_folder.parent

    async def test_iter_jobs(self, async_folder):
        assert len([j async for j in async_folder(2)]) == 5
        assert len([j async for j in async_folder]) == 4
        assert await async_folder['job']


class TestAsyncProject:
    async def test_name(self, async_job):
        assert async_job.name == 'job'
        assert async_job.full_name == 'async_folder/job'
        assert async_job.full_display_name == 'async_folder » job'

    async def test_get_parameters(self, async_args_job):
        assert (await async_args_job.get_parameters())[0]['name'] == 'ARG1'

    async def test_get_build(self, async_job):
        assert await async_job.get(0) is None
        assert await async_job[1]

    async def test_get_special_build(self, async_job):
        assert await async_job.get_first_build()
        assert await async_job.get_last_failed_build() is None

    async def test_iter_build(self, async_job):
        assert len([b async for b in async_job]) == 2
        assert len([b async for b in async_job.iter_builds()]) == 2

    async def test_iter_all_builds(self, async_job):
        assert len([b async for b in async_job.iter_all_builds()]) == 2

    async def test_building(self, async_job):
        assert await async_job.building == False

    async def test_set_next_build_number(self, async_job):
        await async_job.set_next_build_number(10)
        assert await async_job.next_build_number == 10

    async def test_filter_builds_by_result(self, async_job):
        assert len([b async for b in async_job.filter_builds_by_result(result='SUCCESS')]) == 2
        assert not [b async for b in async_job.filter_builds_by_result(result='ABORTED')]
        with pytest.raises(ValueError):
            assert [b async for b in async_job.filter_builds_by_result(result='not a status')] == 'x'
