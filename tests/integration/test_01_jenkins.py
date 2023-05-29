import pytest
from api4jenkins import Folder
from api4jenkins.job import WorkflowJob
from api4jenkins.exceptions import BadRequestError, ItemNotFoundError
import contextlib


@contextlib.contextmanager
def new_job(jenkins, name, conf, recursive):
    try:
        yield jenkins.create_job(name, conf, recursive)
    finally:
        jenkins.delete_job(name)


class TestJenkins:

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

    @pytest.mark.parametrize('params', [{}, {'delay': 2}],
                             ids=['without delay', 'with delay'])
    def test_build_job_without_params(self, job, retrive_build_and_output, params):
        item = job.build(**params)
        build, output = retrive_build_and_output(item)
        assert build == job.get_last_build()
        assert 'true' in ''.join(output)

    @pytest.mark.parametrize('params', [{'ARG1': 'arg1_value'},
                                        {'ARG1': 'arg1_value', 'delay': 2}],
                             ids=['without delay', 'with delay'])
    def test_build_job_with_params(self, args_job, retrive_build_and_output, params):
        item = args_job.build(**params)
        build, output = retrive_build_and_output(item)
        assert build == args_job.get_last_build()
        assert params['ARG1'] in ''.join(output)

    def test_iter_jobs(self, jenkins):
        assert len(list(jenkins.iter_jobs())) == 1
        assert len(list(jenkins.iter_jobs(2))) == 6
        assert len(list(jenkins)) == 1
        assert len(list(jenkins(2))) == 6

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
