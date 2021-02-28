# encoding: utf-8
import pytest
from api4jenkins.exceptions import BadRequestError
from api4jenkins.job import Folder


class TestFolder:

    @pytest.mark.parametrize('name, exception', [('Level2_Folder1', "A job already exists "
                                                  "with the name  Level2_Folder1"),
                                                 ('ab@cd', '@  is an unsafe character')],
                             ids=['exist', 'unsafe'])
    def test_create_fail(self, folder, name, exception):
        with pytest.raises(BadRequestError, match=exception):
            folder.create(name, '')

    def test_create_succ(self, folder, folder_xml):
        folder.create('new_job', folder_xml)
        assert folder.get('new_job')

    @pytest.mark.parametrize('name,type_', [('not exist', type(None)),
                                            ('Level2_Folder1', Folder)])
    def test_get(self, folder, name, type_):
        assert isinstance(folder.get(name), type_)
        assert isinstance(folder[name], type_)

    def test_iter(self, folder):
        assert len(list(folder.iter())) == 1
        assert len(list(folder)) == 1

    @pytest.mark.parametrize('name, exception', [('Level2_Folder1', "A job already exists "
                                                  "with the name  Level2_Folder1"),
                                                 ('not exist', 'No such job: not exist')],
                             ids=['job exist', 'no source job'])
    def test_copy_fail(self, folder, name, exception):
        with pytest.raises(BadRequestError, match=exception):
            folder.copy(name, name)

    def test_copy_succ(self, folder):
        folder.copy('Level2_Folder1', 'new_folder')
        assert folder.get('new_folder')

    def test_move(self, folder, folder_xml):
        folder.create('new_folder', folder_xml)
        new_folder = folder.get('new_folder')
        new_folder.move('Level1_Folder1/Level2_Folder1')
        moved = folder.get('Level2_Folder1').get('new_folder')
        assert new_folder.exists()
        assert folder.get('new_folder') is None
        assert moved == new_folder

    def test_rename(self, folder, folder_xml):
        folder.create('new_folder', folder_xml)
        new_folder = folder.get('new_folder')
        new_folder.rename('new_folder_rename')
        renamed = folder.get('new_folder_rename')
        assert new_folder.exists()
        assert folder.get('new_folder') is None
        assert renamed == new_folder

    def test_delete(self, folder):
        folder.delete()
        assert folder.exists() is False

    def test_parent(self, folder, jenkins):
        job = folder.get('Level2_Folder1')
        assert folder == job.parent
        assert jenkins == folder.parent

    @pytest.mark.xfail
    def test_credential(self, folder, credential_xml):
        assert len(list(folder.credentials)) == 0
        folder.credentials.create(credential_xml)
        assert len(list(folder.credentials)) == 1
        c = folder.credentials.get('user-id')
        assert c.id == 'user-id'
        c.delete()
        assert c.exists() == False

    def test_view(self, folder, view_xml):
        assert len(list(folder.views)) == 1
        folder.views.create('test-view', view_xml)
        assert len(list(folder.views)) == 2
        v = folder.views.get('test-view')
        assert v.name == 'test-view'
        assert len(list(v)) == 0
        v.include('Level2_Folder1')
        assert len(list(v)) == 1
        job = v.get_job('Level2_Folder1')
        assert job.name == 'Level2_Folder1'
        v.exclude('Level2_Folder1')
        assert len(list(v)) == 0
        v.delete()
        assert v.exists() == False

class TestProject:

    @pytest.mark.parametrize('params', [{}, {'delay': 2}],
                             ids=['without delay', 'with delay'])
    def test_build_without_params(self, workflow, params, retrive_build_and_output):
        item = workflow.build(**params)
        build, output = retrive_build_and_output(item)
        assert build == workflow.get_last_build()
        assert workflow.jenkins.version in ''.join(output)

    @pytest.mark.parametrize('params', [{'arg1': 'arg1_value'},
                                        {'arg1': 'arg1_value', 'delay': 2}],
                             ids=['without delay', 'with delay'])
    def test_build_with_params(self, freejob, params, retrive_build_and_output):
        item = freejob.build(**params)
        build, output = retrive_build_and_output(item)
        assert build == freejob.get_last_build()
        assert params['arg1'] in ''.join(output)

    def test_get_build(self, workflow):
        build = workflow.get_build(1)
        assert build == workflow.get_first_build()
