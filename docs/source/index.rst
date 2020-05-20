.. Jenkinsx documentation master file, created by
   sphinx-quickstart on Mon Dec 16 20:16:12 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Jenkinsx's documentation!
====================================


`Jenkinsx <https://github.com/joelee2012/jenkinsx>`_ is an object oriented `Python <https://www.python.org/>`_ project that provides access to the `Jenkins <https://jenkins.io/>`_ `Remote access API <https://wiki.jenkins.io/display/JENKINS/Remote+access+API>`_ programmatically. It assiciates/constructs python class/object with Jenkins's items and JSON API.

------------------------------


It provides but not limits functionalities to control Job, Build, Node, View, Credential, BuildQueue, Plugins and System:

- get/delete/create/move/rename/copy/build/enable/disable job or folder, iterate children jobs with depth, folder based views/credentials functionalities
- get/iterate builds of project, stop/term/kill build, get progressive console output.
- get/delete/create/iterate views for jenkins or folder. add/remove jobs to/from view.
- get/delete/create/iterate credentials for system or folder.
- get/delete/create/iterate nodes, run groovy script on node.
- get/cancel/iterate queue item, get job/build from queue item.
- restart/safe restart/quiet down/cancel quiet down/run groovy script for master
- get item status(int, bool, str) by accessing attribute of python object.
- install/uninstall/iterate plugin, check installation status, change update site and set proxy


Quick start
----------------------------------------

Here is an example to create job and start build, obtain build object the queue item, and pull progressive output until its completion, and obtain the build status.


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


.. toctree::
   :maxdepth: 2
   :caption: Contents:

  user/install.rst
  user/example.rst
  user/api.rst



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
