# encoding: utf-8
import asyncio
import threading
from importlib import import_module

from httpx import HTTPStatusError

from api4jenkins.mix import UrlMixIn

from .credential import AsyncCredentials, Credentials
from .exceptions import ItemNotFoundError
from .http import new_async_http_client, new_http_client
from .item import AsyncItem, Item
from .job import AsyncFolder, AsyncProject, Folder
from .node import AsyncNodes, Nodes
from .plugin import AsyncPluginsManager, PluginsManager
from .queue import AsyncQueue, Queue
from .system import AsyncSystem, System
from .user import AsyncUser, AsyncUsers, User, Users
from .view import AsyncViews, Views

EMPTY_FOLDER_XML = '''<?xml version='1.0' encoding='UTF-8'?>
<com.cloudbees.hudson.plugins.folder.Folder/>'''


class Jenkins(Item, UrlMixIn):
    r'''Constructs  :class:`Jenkins <Jenkins>`.

    :param url: URL of Jenkins server, ``str``
    :param auth: (optional) Auth ``tuple`` to enable Basic/Digest/Custom HTTP Auth.
    :param \*\*kwargs: other kwargs are same as `httpx.Client <https://www.python-httpx.org/api/#client>`_

    Usage::

        >>> from api4jenkins import Jenkins
        >>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
        >>> print(j)
        <Jenkins: http://127.0.0.1:8080/>
        >>> j.version
        '2.176.2'
    '''

    def __init__(self, url, **kwargs):
        self.http_client = new_http_client(**kwargs)
        self._crumb = None
        self._auth = kwargs.get('auth')
        self._sync_lock = threading.Lock()
        super().__init__(self, url)
        self.user = User(
            self, f'{self.url}user/{self._auth[0]}/') if self._auth else None

    def get_job(self, full_name):
        '''Get job by full name

        :param full_name: ``str``, full name of job
        :returns: Corresponding Job object or None

        Usage::

            >>> from api4jenkins import Jenkins
            >>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
            >>> job = j.get_job('freestylejob')
            >>> print(job)
            <FreeStyleProject: http://127.0.0.1:8080/job/freestylejob/>
        '''
        folder, name = self._resolve_name(full_name)
        if folder.exists():
            return folder.get(name)

    def iter(self, depth=0):
        '''Iterate jobs with depth

        :param depth: ``int``, depth to iterate, default is 0
        :returns: iterator of jobs

        Usage::

            >>> from api4jenkins import Jenkins
            >>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
            >>> for job in j.iter():
            ...     print(job)
            <FreeStyleProject: http://127.0.0.1:8080/job/freestylejob/>
            ...
        '''
        yield from Folder(self, self.url)(depth)

    def create_job(self, full_name, xml, recursive=False):
        '''Create new jenkins job with given xml configuration

        :param full_name: ``str``, full name of job
        :param xml: xml configuration string
        :param recursive: (optional) Boolean, recursively create folder if not existed

        Usage::

            >>> from api4jenkins import Jenkins
            >>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
            >>> xml = """<?xml version='1.1' encoding='UTF-8'?>
            ... <project>
            ...   <builders>
            ...     <hudson.tasks.Shell>
            ...       <command>echo $JENKINS_VERSION</command>
            ...     </hudson.tasks.Shell>
            ...   </builders>
            ... </project>"""
            >>> j.create_job('freestylejob', xml)
            >>> job = j.get_job('freestylejob')
            >>> print(job)
            <FreeStyleProject: http://127.0.0.1:8080/job/freestylejob/>
        '''
        folder, name = self._resolve_name(full_name)
        if recursive and not folder.exists():
            self.create_job(folder.full_name, EMPTY_FOLDER_XML,
                            recursive=recursive)
        return folder.create(name, xml)

    def copy_job(self, full_name, dest):
        '''Create job by copying other job, the source job and dest job are in
        same folder.

        :param full_name: full name of source job
        :param dest: name of new job

        Usage::

            >>> from api4jenkins import Jenkins
            >>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
            >>> j.copy_job('folder/freestylejob', 'newjob')
            >>> j.get_job('folder/newjob')
            >>> print(job)
            <FreeStyleProject: http://127.0.0.1:8080/job/folder/job/newjob/>
        '''
        folder, name = self._resolve_name(full_name)
        return folder.copy(name, dest)

    def delete_job(self, full_name):
        '''Delete job

        :param full_name: ``str``, full name of job

        Usage::

            >>> from api4jenkins import Jenkins
            >>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
            >>> job = j.get_job('freestylejob')
            >>> print(job)
            <FreeStyleProject: http://127.0.0.1:8080/job/freestylejob/>
            >>> j.delete_job('freestylejob')
            >>> job = j.get_job('freestylejob')
            >>> print(job)
            None
        '''
        if job := self.get_job(full_name):
            job.delete()

    def build_job(self, full_name, **params):
        '''Build job with/without params

        :param full_name: ``str``, full name of job
        :param params: parameters for building, support delay and remote token
        :returns: ``QueueItem``

        Usage::

            >>> from api4jenkins import Jenkins
            >>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
            >>> item = j.build_job('freestylejob')
            >>> import time
            >>> while not item.get_build():
            ...      time.sleep(1)
            >>> build = item.get_build()
            >>> print(build)
            <FreeStyleBuild: http://127.0.0.1:8080/job/freestylejob/1/>
            >>> for line in build.progressive_output():
            ...     print(line)
            ...
        '''
        job = self._get_job_and_check(full_name)
        return job.build(**params)

    def _get_job_and_check(self, full_name):
        job = self.get_job(full_name)
        if job is None:
            raise ItemNotFoundError(f'No such job: {full_name}')
        return job

    def rename_job(self, full_name, new_name):
        job = self._get_job_and_check(full_name)
        return job.rename(new_name)

    def move_job(self, full_name, new_full_name):
        job = self._get_job_and_check(full_name)
        return job.move(new_full_name)

    def duplicate_job(self, full_name, new_name, recursive=False):
        job = self._get_job_and_check(full_name)
        return job.duplicate(new_name, recursive)

    def is_name_safe(self, name):
        resp = self.handle_req('GET', 'checkJobName', params={'value': name})
        return 'is an unsafe character' not in resp.text

    def validate_jenkinsfile(self, content):
        """validate Jenkinsfile, see
        https://www.jenkins.io/doc/book/pipeline/development/#linter

        Args:
            content (str): content of Jenkinsfile

        Returns:
            str: 'Jenkinsfile successfully validated.' if validate successful
            or error message
        """
        data = {'jenkinsfile': content}
        return self.handle_req(
            'POST', 'pipeline-model-converter/validate', data=data).text

    def _resolve_name(self, full_name):
        parent, name = self._parse_name(full_name)
        return Folder(self, self._name2url(parent)), name

    # def exists(self):
    #     '''Check if Jenkins server is up

    #     :returns: True or False
    #     '''
    #     try:
    #         self._request('HEAD', self.url)
    #         return True
    #     except Exception as e:
    #         return isinstance(e, (AuthenticationError, PermissionError))

    @property
    def crumb(self):
        '''Crumb of Jenkins'''
        if self._crumb is None:
            with self._sync_lock:
                if self._crumb is None:
                    try:
                        _crumb = self._request(
                            'GET', f'{self.url}crumbIssuer/api/json').json()
                        self._crumb = {
                            _crumb['crumbRequestField']: _crumb['crumb']}
                    except HTTPStatusError:
                        self._crumb = {}
        return self._crumb

    @property
    def system(self):
        '''An object for managing system operation.
        see :class:`System <api4jenkins.system.System>`'''
        return System(self, self.url)

    @property
    def plugins(self):
        '''An object for managing plugins.
        see :class:`PluginsManager <api4jenkins.plugin.PluginsManager>`'''
        return PluginsManager(self, f'{self.url}pluginManager/')

    @property
    def version(self):
        '''Version of Jenkins'''
        return self.handle_req('HEAD', '').headers['X-Jenkins']

    @property
    def credentials(self):
        '''An object for managing credentials.
        see :class:`Credentials <api4jenkins.credential.Credentials>`'''
        return Credentials(self, f'{self.url}credentials/store/system/')

    @property
    def views(self):
        '''An object for managing views of main window.
        see :class:`Views <api4jenkins.view.Views>`'''
        return Views(self)

    @property
    def nodes(self):
        '''An object for managing nodes.
        see :class:`Nodes <api4jenkins.node.Nodes>`'''
        return Nodes(self, f'{self.url}computer/')

    @property
    def queue(self):
        '''An object for managing build queue.
        see :class:`Queue <api4jenkins.queue.Queue>`'''
        return Queue(self, f'{self.url}queue/')

    @property
    def users(self):
        return Users(self, f'{self.url}asynchPeople/')

    @property
    def me(self):
        return self.user

    def __call__(self, depth):
        yield from self.iter(depth)

    def __getitem__(self, full_name):
        return self.get_job(full_name)


def _patch_to(module, cls, func=None):
    _module = import_module(module)
    if func:
        _class = getattr(_module, cls.__name__)
        setattr(_class, func.__name__, func)
    else:
        setattr(_module, cls.__name__, cls)


class AsyncJenkins(AsyncItem, UrlMixIn):

    def __init__(self, url, **kwargs):
        self.http_client = new_async_http_client(**kwargs)
        self._crumb = None
        self._async_lock = asyncio.Lock()
        self._auth = kwargs.get('auth')
        super().__init__(self, url)
        self.user = AsyncUser(
            self, f'{self.url}user/{self._auth[0]}/') if self._auth else None

    async def get_job(self, full_name):
        folder, name = self._resolve_name(full_name)
        if await folder.exists():
            return await folder.get(name)

    async def aiter(self, depth=0):
        async for job in AsyncFolder(self, self.url)(depth):
            yield job

    async def create_job(self, full_name, xml, recursive=False):
        folder, name = self._resolve_name(full_name)
        if recursive and not await folder.exists():
            await self.create_job(folder.full_name, EMPTY_FOLDER_XML,
                                  recursive=recursive)
        return await folder.create(name, xml)

    async def copy_job(self, full_name, dest):
        folder, name = self._resolve_name(full_name)
        return await folder.copy(name, dest)

    async def delete_job(self, full_name):
        job = await self.get_job(full_name)
        if job:
            await job.delete()

    async def build_job(self, full_name, **params):
        job = await self._get_job_and_check(full_name)
        if not isinstance(job, AsyncProject):
            raise AttributeError(f'{job} has no attribute build')
        return await job.build(**params)

    async def rename_job(self, full_name, new_name):
        job = await self._get_job_and_check(full_name)
        return await job.rename(new_name)

    async def move_job(self, full_name, new_full_name):
        job = await self._get_job_and_check(full_name)
        return await job.move(new_full_name)

    async def duplicate_job(self, full_name, new_name, recursive=False):
        job = await self._get_job_and_check(full_name)
        return await job.duplicate(new_name, recursive)

    async def _get_job_and_check(self, full_name: str):
        job = await self.get_job(full_name)
        if job is None:
            raise ItemNotFoundError(f'No such job: {full_name}')
        return job

    async def is_name_safe(self, name):
        resp = await self.handle_req('GET', 'checkJobName', params={'value': name})
        return 'is an unsafe character' not in resp.text

    async def validate_jenkinsfile(self, content):
        data = await self.handle_req(
            'POST', 'pipeline-model-converter/validate', data={'jenkinsfile': content})
        return data.text

    def _resolve_name(self, full_name):
        parent, name = self._parse_name(full_name)
        return AsyncFolder(self, self._name2url(parent)), name

    # async def exists(self):
    #     try:
    #         await self._request('HEAD', self.url)
    #         return True
    #     except Exception as e:
    #         return isinstance(e, (AuthenticationError, PermissionError))

    @property
    async def crumb(self):
        if self._crumb is None:
            async with self._async_lock:
                if self._crumb is None:
                    try:
                        _crumb = (await self._request('GET', f'{self.url}crumbIssuer/api/json')).json()
                        self._crumb = {
                            _crumb['crumbRequestField']: _crumb['crumb']}
                    except HTTPStatusError:
                        self._crumb = {}
        return self._crumb

    @property
    def system(self):
        return AsyncSystem(self, self.url)

    @property
    def plugins(self):
        return AsyncPluginsManager(self, f'{self.url}pluginManager/')

    @property
    async def version(self):
        return (await self.handle_req('HEAD', '')).headers['X-Jenkins']

    @property
    def credentials(self):
        return AsyncCredentials(self, f'{self.url}credentials/store/system/')

    @property
    def views(self):
        return AsyncViews(self)

    @property
    def nodes(self):
        return AsyncNodes(self, f'{self.url}computer/')

    @property
    def queue(self):
        return AsyncQueue(self, f'{self.url}queue/')

    @property
    def users(self):
        return AsyncUsers(self, f'{self.url}asynchPeople/')

    @property
    def me(self):
        return self.user

    async def __call__(self, depth):
        async for job in self.aiter(depth):
            yield job

    async def __getitem__(self, full_name):
        return await self.get_job(full_name)
