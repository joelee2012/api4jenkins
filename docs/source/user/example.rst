.. _example:

Examples
========


Initialization
----------------------------------------


.. code-block:: python

    >>> from api4jenkins import Jenkins
    >>> j = Jenkins('http://127.0.0.1:8080/', auth=('myuser', 'mypassword'))
    >>> j.version
    '2.176.2'
    >>> j.description
    'My jenkins'
    >>> j.attrs
    ['_class', 'mode', 'node_description', 'node_name', 'num_executors', 'description', 'quieting_down', 'slave_agent_port', 'use_crumbs', 'use_security']



Job
------------------------------------

- Get job

.. code-block:: python

    >>> from api4jenkins import Jenkins
    >>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
    >>> job = j.get_job('freestylejob')
    >>> print(job)
    <FreeStyleProject: http://127.0.0.1:8080/job/freestylejob/>

- Create job

.. code-block:: python

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

- Copy job

.. code-block:: python

    >>> from api4jenkins import Jenkins
    >>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
    >>> j.copy_job('freestylejob', 'newjob')
    >>> j.get_job('newjob')
    >>> print(job)
    <FreeStyleProject: http://127.0.0.1:8080/job/newjob/>

- Build job without parameters and pull pregressive output

.. code-block:: python

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

Build job with delay or token

.. code-block:: python

    >>> item = j.build_job('freestylejob', {'delay':'30sec', 'token':'abc'})

Build job with parameters

.. code-block:: python

    >>> item = j.build_job('freestylejob', {'arg1':'string1', 'arg2':'string2'})

- Iterate jobs

Default depth is 0

.. code-block:: python

    >>> from api4jenkins import Jenkins
    >>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
    >>> for job in j.iter_job():
    ...     print(job)
    <FreeStyleProject: http://127.0.0.1:8080/job/freestylejob/>

- Delete job

.. code-block:: python

    >>> from api4jenkins import Jenkins
    >>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
    >>> job = j.get_job('freestylejob')
    >>> print(job)
    <FreeStyleProject: http://127.0.0.1:8080/job/freestylejob/>
    >>> j.delete_job('freestylejob')
    >>> job = j.get_job('freestylejob')
    >>> print(job)
    None

:class:`Folder <api4jenkins.job.Folder>`
-----------------------------------------------------

Requires the `Cloudbees Folders Plugin
<https://wiki.jenkins-ci.org/display/JENKINS/CloudBees+Folders+Plugin>`_ for
Jenkins.

This is an example showing how to create, configure and delete Jenkins folders.


- Create job

Use method :class:`Jenkins.create_job <api4jenkins.Jenkins.create_job>`

.. code-block:: python

    >>> from api4jenkins import Jenkins
    >>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
    >>> j.create_job('folder', folder_xml)
    >>> j.create_job('folder/freestylejob', job_xml)
    >>> job = j.get_job('folder/freestylejob')
    >>> print(job)
    <FreeStyleProject: http://127.0.0.1:8080/job/folder/job/freestylejob/>

Use method :class:`Folder.create <api4jenkins.job.Folder.create>`

    >>> j.create_job('folder', folder_xml)
    >>> folder = j.get_job('folder')
    >>> print(folder)
    <Folder: http://127.0.0.1:8080/job/folder/>
    >>> folder.create('freestylejob', job_xml)
    >>> job = folder.get('freestylejob')
    >>> print(job)
    <FreeStyleProject: http://127.0.0.1:8080/job/folder/job/freestylejob/>

- Copy job


use method :class:`Jenkins.copy_job <api4jenkins.Jenkins.copy_job>`
to copy job in same folder

    >>> from api4jenkins import Jenkins
    >>> j = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
    >>> j.copy_job('folder/freestylejob', 'newjob')
    >>> j.get_job('folder/newjob')
    >>> print(job)
    <FreeStyleProject: http://127.0.0.1:8080/job/folder/job/newjob/>

use method of :class:`Folder.copy <api4jenkins.job.Folder.copy>`
to copy job in same folder

    >>> folder = j.get_job('folder')
    >>> folder.copy('freestylejob', 'newjob')
    >>> job = folder.get('newjob')
    >>> print(job)
    <FreeStyleProject: http://127.0.0.1:8080/job/folder/job/newjob/>

use method of :class:`Job.duplicate <api4jenkins.job.Job.duplicate>`
to copy job in different place

    >>> old = j.get_job('folder/freestylejob')
    >>> old.duplicate('folder/newjob')
    >>> job = j.get_job('folder/newjob')
    >>> print(job)
    <FreeStyleProject: http://127.0.0.1:8080/job/folder/job/newjob/>

