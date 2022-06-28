# encoding: utf-8
import weakref
from importlib import import_module
from pathlib import PurePosixPath

from requests.exceptions import ConnectionError, HTTPError

from .__version__ import (__author__, __author_email__, __copyright__,
                          __description__, __license__, __title__, __url__,
                          __version__)
from .credential import Credentials
from .exceptions import ItemNotFoundError, AuthenticationError
from .item import Item
from .job import Folder
from .node import Nodes
from .plugin import PluginsManager
from .queue import Queue
from .requester import Requester
from .system import System
from .user import User, Users
from .view import Views

EMPTY_FOLDER_XML = '''<?xml version='1.0' encoding='UTF-8'?>
<com.cloudbees.hudson.plugins.folder.Folder/>'''


class Jenkins(Item):
    r'''Constructs  :class:`Jenkins <Jenkins>`.

    :param url: URL of Jenkins server, ``str``
    :param auth: (optional) Auth ``tuple`` to enable Basic/Digest/Custom HTTP Auth.
    :param token: (optional) Boolean, Create user token when initialize instance and
        revoke token once instance is destroied. useful when LDAP server refuse
        username and password used too much often. Defaults to ``False``.
    :param \*\*kwargs: other kwargs are same as `requests.Session.request <https://requests.readthedocs.io/en/latest/api/#requests.Session.request>`_

    Usage::

        >>> from api4jenkins import Jenkins
        >>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
        >>> print(j)
        <Jenkins: http://127.0.0.1:8080/>
        >>> j.version
        '2.176.2'
    '''

    def __init__(self, url, **kwargs):
        token = kwargs.pop('token', None)
        self.send_req = Requester(**kwargs)
        super().__init__(self, url)
        self._crumb = None
        self._token = None
        self._auth = kwargs.get('auth', None)
        self.user = None
        if self._auth:
            self.user = User(self, f'{self.url}user/{self._auth[0]}/')
        if self._auth and token is True:
            self._token = self.user.generate_token()
            weakref.finalize(self.user, self.user.revoke_token,
                             self._token.uuid)
            kwargs['auth'] = (self._auth[0], self._token.value)
            self.send_req = Requester(**kwargs)

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

    def iter_jobs(self, depth=0):
        '''Iterate jobs with depth

        :param depth: ``int``, depth to iterate, default is 0
        :returns: iterator of jobs

        Usage::

            >>> from api4jenkins import Jenkins
            >>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
            >>> for job in j.iter_jobs():
            ...     print(job)
            <FreeStyleProject: http://127.0.0.1:8080/job/freestylejob/>
            ...
        '''
        folder = Folder(self, self.url)
        yield from folder.iter(depth)

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
            self.create_job(folder.full_name, EMPTY_FOLDER_XML, recursive=recursive)
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
        job = self.get_job(full_name)
        if job:
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
        job = self.get_job(full_name)
        if job is None:
            raise ItemNotFoundError(f'No such job: {full_name}')
        return job.build(**params)

    def check_job_name(self, name):
        resp = self.handle_req('GET', 'checkJobName', params={'value': name})
        return 'is an unsafe character' in resp.text

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

    def _url2name(self, url):
        '''Covert job url to full name

        :param url: ``str``, url of job
        :returns: ``str``, full name of job
        '''
        if not url.startswith(self.url):
            raise ValueError(f'{url} is not in {self.url}')
        return url.replace(self.url, '/').replace('/job/', '/').strip('/')

    def _name2url(self, full_name):
        '''Covert job full name to url

        :param full_name: ``str``, full name of job
        :returns: ``str``, url of job
        '''
        if not full_name:
            return self.url
        full_name = full_name.strip('/').replace('/', '/job/')
        return f'{self.url}job/{full_name}/'

    def _resolve_name(self, full_name):
        '''Resolve folder and job name from full name'''
        if full_name.startswith(('http://', 'https://')):
            full_name = self._url2name(full_name)
        path = PurePosixPath(full_name)
        parent = str(path.parent) if path.parent.name else ''
        return Folder(self, self._name2url(parent)), path.name

    def exists(self):
        '''Check if Jenkins server is up

        :returns: Ture or False
        '''
        try:
            self.send_req('GET', self.url)
            return True
        except ConnectionError:
            return False
        except HTTPError as e:
            return e.response.status_code in [401, 403]

    @property
    def crumb(self):
        '''Crumb of Jenkins'''
        if self._crumb is None:
            try:
                _crumb = self.send_req(
                    'GET', f'{self.url}crumbIssuer/api/json').json()
                self._crumb = {_crumb['crumbRequestField']: _crumb['crumb']}
            except HTTPError as e:
                if e.response.status_code in [401, 403]:
                    raise AuthenticationError(
                        f'Invalid authorization for {self}') from e
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
        return self.handle_req('GET', '').headers['X-Jenkins']

    @property
    def credentials(self):
        '''An object for managing credentials.
        see :class:`Credentials <api4jenkins.credential.Credentials>`'''
        return Credentials(self,
                           f'{self.url}credentials/store/system/domain/_/')

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

    def __iter__(self):
        yield from self.iter_jobs()

    def __call__(self, depth):
        yield from self.iter_jobs(depth)

    def __getitem__(self, full_name):
        return self.get_job(full_name)


def _patch_to(module, cls, func=None):
    _module = import_module(module)
    if func:
        _class = getattr(_module, cls.__name__)
        setattr(_class, func.__name__, func)
    else:
        setattr(_module, cls.__name__, cls)
