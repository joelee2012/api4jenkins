import pytest
from api4jenkins import Folder, AsyncFolder
from api4jenkins.job import WorkflowJob, AsyncWorkflowJob
from api4jenkins.exceptions import BadRequestError, ItemNotFoundError

jenkinsfile = '''pipeline {
  agent any
  stages {
    stage ('Initialize') {
      steps {
        echo 'Placeholder.'
      }
    }
  }
}
'''


class TestJenkins:

    def test_me(self, jenkins):
        assert jenkins.me.id == 'admin'

    def test_exists(self, jenkins):
        assert jenkins.exists()

    @pytest.mark.parametrize('name,type_', [('not exist', type(None)),
                                            ('folder', Folder),
                                            ('folder/job', WorkflowJob),
                                            ('folder/not exist', type(None))])
    def test_get_job(self, jenkins, name, type_):
        assert isinstance(jenkins.get_job(name), type_)
        assert isinstance(jenkins[name], type_)

    @pytest.mark.parametrize('name, exception', [('folder', "A job already exists "
                                                  "with the name  folder"),
                                                 ('ab@cd', '@  is an unsafe character')],
                             ids=['exist', 'unsafe'])
    def test_create_job_fail(self, jenkins, name, exception):
        with pytest.raises(BadRequestError, match=exception):
            jenkins.create_job(name, '')

    def test_copy_job(self, jenkins, job):
        jenkins.copy_job(job.full_name, 'copied_job')
        assert jenkins['folder/copied_job']
        jenkins.delete_job('folder/copied_job')

    def test_duplicate_job(self, jenkins, job):
        jenkins.duplicate_job(job.full_name, 'folder/duplicated_job')
        assert jenkins['folder/duplicated_job']
        jenkins.delete_job('folder/duplicated_job')

    @pytest.mark.parametrize('name, exception', [('not exist', ItemNotFoundError),
                                                 ('folder', AttributeError)])
    def test_build_job_fail(self, jenkins, name, exception):
        with pytest.raises(exception):
            jenkins.build_job(name)

    @pytest.mark.parametrize('params', [{}, {'delay': 1}],
                             ids=['without delay', 'with delay'])
    def test_build_job_without_params(self, job, retrive_build_and_output, params):
        item = job.build(**params)
        build, output = retrive_build_and_output(item)
        assert build == job.get_last_build()
        assert 'true' in ''.join(output)

    @pytest.mark.parametrize('params', [{'ARG1': 'arg1_value'},
                                        {'ARG1': 'arg1_value', 'delay': 1}],
                             ids=['without delay', 'with delay'])
    def test_build_job_with_params(self, args_job, retrive_build_and_output, params):
        item = args_job.build(**params)
        build, output = retrive_build_and_output(item)
        assert build == args_job.get_last_build()
        assert params['ARG1'] in ''.join(output)

    def test_iter_jobs(self, jenkins):
        assert len(list(jenkins.iter_jobs())) == 2
        assert len(list(jenkins.iter_jobs(2))) == 12
        assert len(list(jenkins)) == 2
        assert len(list(jenkins(2))) == 12

    def test_rename_job(self, jenkins):
        jenkins.rename_job('folder/for_rename', 'renamed_folder')
        assert jenkins['folder/for_rename'] is None
        assert jenkins['folder/renamed_folder']

    def test_move_job(self, jenkins):
        src = 'folder/for_move'
        assert jenkins[src]
        jenkins.move_job(src, 'folder/folder')
        assert jenkins[src] is None
        assert jenkins['folder/folder/for_move']

    def test_credential(self, jenkins):
        c = jenkins.credentials.get('user-id')
        assert c.id == 'user-id'

    def test_is_name_safe(self, jenkins):
        assert jenkins.is_name_safe('illegal@x') == False
        assert jenkins.is_name_safe('legal')

    def test_validate_jenkinsfile(self, jenkins):
        assert jenkins.validate_jenkinsfile(
            'xxx') != 'Jenkinsfile successfully validated.\n'
        assert jenkins.validate_jenkinsfile(
            jenkinsfile) == 'Jenkinsfile successfully validated.\n'


class TestAsyncJenkins:

    async def test_me(self, async_jenkins):
        assert await async_jenkins.me.id == 'admin'

    async def test_exists(self, async_jenkins):
        assert await async_jenkins.exists()

    @pytest.mark.parametrize('name,type_', [('not exist', type(None)),
                                            ('async_folder', AsyncFolder),
                                            ('async_folder/job', AsyncWorkflowJob),
                                            ('async_folder/not exist', type(None))])
    async def test_get_job(self, async_jenkins, name, type_):
        assert isinstance(await async_jenkins.get_job(name), type_)
        assert isinstance(await async_jenkins[name], type_)

    @pytest.mark.parametrize('name, exception', [('async_folder', "A job already exists "
                                                  "with the name  async_folder"),
                                                 ('ab@cd', '@  is an unsafe character')],
                             ids=['exist', 'unsafe'])
    async def test_create_job_fail(self, async_jenkins, name, exception):
        with pytest.raises(BadRequestError, match=exception):
            await async_jenkins.create_job(name, '')

    async def test_copy_job(self, async_jenkins, async_job):
        await async_jenkins.copy_job(async_job.full_name, 'copied_job')
        assert (await async_jenkins['async_folder/copied_job'])
        await async_jenkins.delete_job('async_folder/copied_job')

    async def test_duplicate_job(self, async_jenkins, async_job):
        await async_jenkins.duplicate_job(async_job.full_name, 'async_folder/duplicated_job')
        assert await async_jenkins['async_folder/duplicated_job']
        await async_jenkins.delete_job('async_folder/duplicated_job')

    @pytest.mark.parametrize('name, exception', [('not exist', ItemNotFoundError),
                                                 ('async_folder', AttributeError)])
    async def test_build_job_fail(self, async_jenkins, name, exception):
        with pytest.raises(exception):
            await async_jenkins.build_job(name)

    @pytest.mark.parametrize('params', [{}, {'delay': 1}],
                             ids=['without delay', 'with delay'])
    async def test_build_job_without_params(self, async_job, async_retrive_build_and_output, params):
        item = await async_job.build(**params)
        build, output = await async_retrive_build_and_output(item)
        assert build == await async_job.get_last_build()
        assert 'true' in ''.join(output)

    @pytest.mark.parametrize('params', [{'ARG1': 'arg1_value'},
                                        {'ARG1': 'arg1_value', 'delay': 1}],
                             ids=['without delay', 'with delay'])
    async def test_build_job_with_params(self, async_args_job, async_retrive_build_and_output, params):
        item = await async_args_job.build(**params)
        build, output = await async_retrive_build_and_output(item)
        assert build == await async_args_job.get_last_build()
        assert params['ARG1'] in ''.join(output)

    async def test_iter_jobs(self, async_jenkins):
        assert len([v async for v in async_jenkins.iter_jobs()]) == 2
        assert len([v async for v in async_jenkins.iter_jobs(2)]) == 12
        assert len([v async for v in async_jenkins]) == 2
        assert len([v async for v in async_jenkins(2)]) == 12

    async def test_rename_job(self, async_jenkins):
        await async_jenkins.rename_job('async_folder/for_rename', 'renamed_folder')
        assert await async_jenkins['async_folder/for_rename'] is None
        assert await async_jenkins['async_folder/renamed_folder']

    async def test_move_job(self, async_jenkins):
        src = 'async_folder/for_move'
        assert await async_jenkins[src]
        await async_jenkins.move_job(src, 'async_folder/folder')
        assert await async_jenkins[src] is None
        assert await async_jenkins['async_folder/folder/for_move']

    async def test_credential(self, async_jenkins):
        c = await async_jenkins.credentials.get('user-id')
        assert await c.id == 'user-id'

    async def test_is_name_safe(self, async_jenkins):
        assert await async_jenkins.is_name_safe('illegal@x') == False
        assert await async_jenkins.is_name_safe('legal')

    async def test_validate_jenkinsfile(self, async_jenkins):
        assert await async_jenkins.validate_jenkinsfile(
            'xxx') != 'Jenkinsfile successfully validated.\n'
        assert await async_jenkins.validate_jenkinsfile(
            jenkinsfile) == 'Jenkinsfile successfully validated.\n'
