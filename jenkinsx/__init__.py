# encoding: utf-8

'''
>>> from jenkinsx import Jenkins
>>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
>>> j.version
'2.176.2'
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
>>> print(job.parent)
<Jenkins: http://127.0.0.1:8080/>
>>> print(job.jenkins)
<Jenkins: http://127.0.0.1:8080/>
>>> import time
>>> item = job.build()
>>> while not item.get_build():
...      time.sleep(1)
>>> build = item.get_build()
>>> print(build)
<FreeStyleBuild: http://127.0.0.1:8080/job/freestylejob/1/>
>>> for line in build.progressive_output():
...     print(line)
...
Started by user admin
Running as SYSTEM
Building in workspace /var/jenkins_home/workspace/freestylejob
[freestylejob] $ /bin/sh -xe /tmp/jenkins2989549474028065940.sh
+ echo $JENKINS_VERSION
2.176.2
Finished: SUCCESS
>>> build.building
False
>>> build.result
'SUCCESS'
'''

from importlib import import_module
from pathlib import PurePosixPath
import time
import weakref

from requests.exceptions import HTTPError

from jenkinsx.system import System

from .__version__ import __author__, __author_email__
from .__version__ import __license__, __copyright__
from .__version__ import __title__, __description__, __url__, __version__
from .credential import Credentials
from .exceptions import ItemNotFoundError
from .item import Item
from .job import Folder
from .node import Nodes
from .plugin import PluginsManager
from .queue import Queue
from .requester import Requester
from .user import User
from .view import Views


class Jenkins(Item):
    '''Constructs  :class:`Jenkins <Jenkins>`

    :param url:
    :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
    :param token: (optional) if Ture, create user token on fly, useful
        when LDAP server refuse username and password used too much often.
    :param max_retries: (optional) The maximum number of retries each
        connection should attempt. default value is 1, more detail can be
        found requests ``HTTPAdapter``.
    :param timeout: (optional) How many seconds to wait for the server to
        send data before giving up, as a float, or a :ref:`(connect timeout,
        read timeout) <timeouts>` tuple.
    :type timeout: float or tuple
    :param allow_redirects: (optional) Boolean. Enable/disable
        GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD redirection.
        Defaults to ``True``.
    :type allow_redirects: bool
    :param proxies: (optional) Dictionary mapping protocol to
        the URL of the proxy.
    :param verify: (optional) Either a boolean, in which case it controls
        whether we verify the server's TLS certificate, or a string,
        in which case it must be a path to a CA bundle to use.
        Defaults to ``True``.
    :param stream: (optional) if ``False``, the response content will be
        immediately downloaded.
    :param cert: (optional) if String, path to ssl client cert file (.pem).
        If Tuple, ('cert', 'key') pair.

    Usage::

        >>> from jenkinsx import Jenkins
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
        if self._auth and token is True:
            user = User(self, f'{self.url}user/{self._auth[0]}/')
            self._token = user.generate_token()
            weakref.finalize(user, user.revoke_token,
                             self._token.uuid)
            kwargs['auth'] = (self._auth[0], self._token.value)
            self.send_req = Requester(**kwargs)

    def get_job(self, full_name):
        '''Get job by full name

        :param full_name: full name of job
        :returns: Corresponding Job object or None

        Usage::
            >>> from jenkinsx import Jenkins
            >>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
            >>> job = j.get_job('freestylejob')
            >>> print(job)
            <FreeStyleProject: http://127.0.0.1:8080/job/freestylejob/>
        '''
        folder, name = self._get_folder(full_name)
        return folder.get_job(name)

    def iter_jobs(self, depth=0):
        '''Iterate jobs with depth

        :param depth: depth of iterate, default is 0
        :returns: iterator of jobs

        Usage::
            >>> from jenkinsx import Jenkins
            >>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
            >>> for job in j.iter_job():
            ...     print(job)
            <FreeStyleProject: http://127.0.0.1:8080/job/freestylejob/>
            ...
        '''
        folder = Folder(self, self.path2url(''))
        yield from folder.iter_jobs(depth)

    def create_job(self, full_name, xml):
        '''Create new jenkins job with given xml configuration

        :param full_name: full name of job
        :param xml: xml configuration string

        Usage::
        >>> from jenkinsx import Jenkins
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
        folder, name = self._get_folder(full_name)
        return folder.create_job(name, xml)

    def copy_job(self, full_name, dest):
        '''Create job by copying other job, the source job and dest job are in
        same folder.

        :param full_name: full name of source job
        :param dest: name of new job

        Usage::
            >>> from jenkinsx import Jenkins
            >>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
            >>> j.copy_job('folder/freestylejob', 'newjob')
            >>> j.get_job('folder/newjob')
            >>> print(job)
            <FreeStyleProject: http://127.0.0.1:8080/job/folder/job/newjob/>
        '''
        folder, name = self._get_folder(full_name)
        return folder.copy_job(name, dest)

    def delete_job(self, full_name):
        '''Delete job

        :param full_name: full name of job

        Usage::
            >>> from jenkinsx import Jenkins
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

    def build_job(self, full_name, parameters=None):
        '''Build job with/without parameters

        :param full_name: full name of job
        :param parameters: None or Dict
        :returns: ``Queue``

        Usage::
            >>> from jenkinsx import Jenkins
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
        return job.build(parameters)

    def url2path(self, url):
        if not url.startswith(self.url):
            raise ValueError(f'{url} is not in {self.url}')
        return url.replace(self.url, '/').replace('/job/', '/')

    def path2url(self, path):
        if not path:
            return self.url
        path = path.strip('/').replace('/', '/job/')
        return f'{self.url}job/{path}/'

    def _get_folder(self, full_name):
        path = PurePosixPath(full_name)
        parent = str(path.parent) if path.parent.name else ''
        return Folder(self, self.path2url(parent)), path.name

    def exists(self):
        '''Check if Jenkins server is up

        :returns: Ture or False
        '''
        try:
            return super().exists()
        except (HTTPError, ConnectionError):
            return False

    @property
    def crumb(self):
        self._add_crumb({})
        return self._crumb

    @property
    def system(self):
        return System(self, self.url)

    @property
    def plugins(self):
        return PluginsManager(self, f'{self.url}pluginManager/')

    @property
    def version(self):
        return self.handle_req('GET', '').headers['X-Jenkins']

    @property
    def credentials(self):
        return Credentials(self,
                           f'{self.url}credentials/store/system/domain/_/')

    @property
    def views(self):
        return Views(self)

    @property
    def nodes(self):
        return Nodes(self, f'{self.url}computer/')

    @property
    def queue(self):
        return Queue(self, f'{self.url}queue/')


def _patch_to(module, cls, func=None):
    _module = import_module(module)
    if func:
        _class = getattr(_module, cls.__name__)
        setattr(_class, func.__name__, func)
    else:
        setattr(_module, cls.__name__, cls)
