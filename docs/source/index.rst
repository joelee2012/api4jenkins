.. api4jenkins documentation master file, created by
   sphinx-quickstart on Mon Dec 16 20:16:12 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Jenkins Python Client
=================================================
.. image:: https://img.shields.io/github/license/joelee2012/api4jenkins
    :target: https://pypi.org/project/api4jenkins/

.. image:: https://img.shields.io/pypi/wheel/api4jenkins
    :target: https://pypi.org/project/api4jenkins/

.. image:: https://img.shields.io/pypi/v/api4jenkins
    :target: https://pypi.org/project/api4jenkins/

.. image:: https://img.shields.io/pypi/pyversions/api4jenkins
    :target: https://pypi.org/project/api4jenkins/



`Python3 <https://www.python.org/>`_ client library for `Jenkins API <https://wiki.jenkins.io/display/JENKINS/Remote+access+API>`_.


Features
--------

    - Object oriented, each Jenkins item has corresponding class, easy to use and extend
    - Base on `api/json`, easy to query/filter attribute of item
    - Setup relationship between class just like Jenkins item
    - Support api for almost every Jenkins item
    - Pythonic
    - Test with latest Jenkins LTS


Quick start
----------------------------------------

Here is an example to create and build job, then monitor progressive output until it's done.


    >>> from api4jenkins import Jenkins
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
