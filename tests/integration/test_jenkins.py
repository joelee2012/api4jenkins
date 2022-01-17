import pytest
from api4jenkins import Folder
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
        assert isinstance(jenkins[name], type_)

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
    def test_build_job_without_params(self, jenkins, workflow, retrive_build_and_output, params):
        item = jenkins.build_job(workflow.name, **params)
        build, output = retrive_build_and_output(item)
        assert build == workflow.get_last_build()
        assert jenkins.version in ''.join(output)

    @pytest.mark.parametrize('params', [{'arg1': 'arg1_value'},
                                        {'arg1': 'arg1_value', 'delay': 2}],
                             ids=['without delay', 'with delay'])
    def test_build_job_with_params(self, jenkins, freejob, retrive_build_and_output, params):
        item = jenkins.build_job(freejob.name, **params)
        build, output = retrive_build_and_output(item)
        assert build == freejob.get_last_build()
        assert params['arg1'] in ''.join(output)

    def test_iter_jobs(self, jenkins):
        assert len(list(jenkins.iter_jobs())) == 1
        assert len(list(jenkins.iter_jobs(2))) == 2
        assert len(list(jenkins)) == 1
        assert len(list(jenkins(2))) == 2

    def test_credential(self, jenkins, credential_xml):
        assert len(list(jenkins.credentials)) == 0
        jenkins.credentials.create(credential_xml)
        assert len(list(jenkins.credentials)) == 1
        c = jenkins.credentials.get('user-id')
        assert c.id == 'user-id'
        c.delete()
        assert c.exists() == False

    def test_view(self, jenkins, view_xml):
        assert len(list(jenkins.views)) == 1
        jenkins.views.create('test-view', view_xml)
        assert len(list(jenkins.views)) == 2
        v = jenkins.views.get('test-view')
        assert v.name == 'test-view'
        assert len(list(v)) == 0
        v.include('Level1_Folder1')
        assert len(list(v)) == 1
        job = v.get_job('Level1_Folder1')
        assert job.name == 'Level1_Folder1'
        v.exclude('Level1_Folder1')
        assert len(list(v)) == 0
        v.delete()
        assert v.exists() == False
