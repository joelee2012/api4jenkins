import pytest
from api4jenkins import Folder
import time
from api4jenkins.exceptions import BadRequestError, ItemNotFoundError


class TestJenkins:

    def test_exists(self, jenkins):
        assert jenkins.exists()

    @pytest.mark.parametrize('name,type_', [('not exist', type(None)),
                                            ('Level1_Folder1', Folder),
                                            ('Level1_Folder1/Level2_Folder1', Folder),
                                            ('Level1_Folder1/not exist', type(None))])
    def test_get_job(self, jenkins, name, type_):
        job = jenkins.get_job(name)
        assert isinstance(job, type_)

    @pytest.mark.parametrize('name, exception', [('Level1_Folder1', "A job already exists "
                                                  "with the name  Level1_Folder1"),
                                                 ('ab@cd', '@  is an unsafe character')],
                             ids=['exist', 'unsafe'])
    def test_create_job_fail(self, jenkins, folder_xml, name, exception):
        with pytest.raises(BadRequestError, match=exception):
            jenkins.create_job(name, folder_xml)

    def test_create_job_succ(self, jenkins, folder_xml):
        jenkins.create_job('Level1_Folder1/new_folder', folder_xml)
        assert jenkins.get_job('Level1_Folder1/new_folder')

    def test_copy_job(self, jenkins):
        jenkins.copy_job('Level1_Folder1/Level2_Folder1', 'new_folder')
        assert jenkins.get_job('Level1_Folder1/new_folder')

    def test_delete_job(self, jenkins):
        assert jenkins.get_job('Level1_Folder1/Level2_Folder1')
        jenkins.delete_job('Level1_Folder1/Level2_Folder1')
        assert jenkins.get_job('Level1_Folder1/Level2_Folder1') is None

    @pytest.mark.parametrize('name, exception', [('not exist', ItemNotFoundError),
                                                 ('Level1_Folder1', AttributeError)])
    def test_build_job_fail(self, jenkins, name, exception):
        with pytest.raises(exception):
            jenkins.build_job(name)

    @pytest.mark.parametrize('params', [{}, {'delay': 2}],
                             ids=['without delay', 'with delay'])
    def test_build_job_without_params(self, jenkins, workflow, params):
        item = jenkins.build_job(workflow.name, params)
        while not item.get_build():
            time.sleep(1)
        build = item.get_build()
        output = []
        for line in build.progressive_output():
            output.append(str(line))
        assert build == workflow.get_last_build()
        assert jenkins.version in ''.join(output)

    @pytest.mark.parametrize('params', [{'arg1': 'arg1_value'},
                                        {'arg1': 'arg1_value', 'delay': 2}],
                             ids=['without delay', 'with delay'])
    def test_build_job_with_params(self, jenkins, freejob, params):
        item = jenkins.build_job(freejob.name, params)
        while not item.get_build():
            time.sleep(1)
        build = item.get_build()
        output = []
        for line in build.progressive_output():
            output.append(str(line))
        assert build == freejob.get_last_build()
        assert params['arg1'] in ''.join(output)

    def test_iter_jobs(self, jenkins):
        assert len(list(jenkins.iter_jobs())) == 1
        assert len(list(jenkins.iter_jobs(2))) == 2
