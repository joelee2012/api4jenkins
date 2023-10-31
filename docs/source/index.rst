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



`Python3 <https://www.python.org/>`_ client library for 
`Jenkins API <https://wiki.jenkins.io/display/JENKINS/Remote+access+API>`_.


Features
--------

- Provides ``sync`` and ``async`` APIs
- Object oriented, each Jenkins item has corresponding class, easy to use and extend
- Base on ``api/json``, easy to query/filter attribute of item
- Setup relationship between class just like Jenkins item
- Support api for almost every Jenkins item
- Pythonic
- Test with latest `Jenkins LTS <https://www.jenkins.io/changelog-stable/>`_


Quick start
----------------------------------------

Here is an example to create and build job, then monitor progressive output 
until it's done.

Sync example::

    >>> from api4jenkins import Jenkins
    >>> client = Jenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
    >>> client.version
    '2.176.2'
    >>> xml = """<?xml version='1.1' encoding='UTF-8'?>
    ... <project>
    ...   <builders>
    ...     <hudson.tasks.Shell>
    ...       <command>echo $JENKINS_VERSION</command>
    ...     </hudson.tasks.Shell>
    ...   </builders>
    ... </project>"""
    >>> client.create_job('path/to/job', xml)
    >>> import time
    >>> item = client.build_job('path/to/job')
    >>> while not item.get_build():
    ...      time.sleep(1)
    >>> build = item.get_build()
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


Async example::

    import asyncio
    import time
    from api4jenkins import AsyncJenkins

    async main():
        client = AsyncJenkins('http://127.0.0.1:8080/', auth=('admin', 'admin'))
        print(await client.version)
        xml = """<?xml version='1.1' encoding='UTF-8'?>
        <project>
        <builders>
            <hudson.tasks.Shell>
            <command>echo $JENKINS_VERSION</command>
            </hudson.tasks.Shell>
        </builders>
        </project>"""
        await client.create_job('job', xml)
        item = await client.build_job('job')
        while not await item.get_build():
            time.sleep(1)
        build = await item.get_build()
        async for line in build.progressive_output():
            print(line)

        print(await build.building)
        print(await build.result)

    asyncio.run(main())


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   user/install
   user/example
   user/api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
