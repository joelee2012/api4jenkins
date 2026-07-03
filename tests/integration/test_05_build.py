# encoding: utf-8
from api4jenkins.build import AsyncStage, Stage


class TestBuild:
    def test_get_job(self, job):
        assert job == job[1].project

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

    def test_iter_stages(self, job):
        build = job[1]
        stages = list(build.iter())
        assert isinstance(stages, list)
        for stage in stages:
            assert isinstance(stage, Stage)
            assert hasattr(stage, 'name')
            assert hasattr(stage, 'status')

    def test_iter_stage_steps(self, job):
        build = job[1]
        for stage in build.iter():
            steps = list(stage)
            assert isinstance(steps, list)
            for step in steps:
                assert hasattr(step, 'name')
                assert hasattr(step, 'status')
            break


class TestAsyncBuild:
    async def test_aiter_stages(self, async_job):
        build = await async_job[1]
        stages = [s async for s in build.aiter()]
        assert isinstance(stages, list)
        for stage in stages:
            assert isinstance(stage, AsyncStage)
            assert hasattr(stage, 'name')
            assert hasattr(stage, 'status')

    async def test_aiter_stage_steps(self, async_job):
        build = await async_job[1]
        async for stage in build.aiter():
            steps = [s async for s in stage]
            assert isinstance(steps, list)
            for step in steps:
                assert hasattr(step, 'name')
                assert hasattr(step, 'status')
            break
