.. _example:

Examples
========

Jenkins
----------------------------------------
The first step is to initialize Jenkins object, it is very simple, just set `url`, `username` and `password` or `api token`:

    >>> from api4jenkins import Jenkins
    >>> j = Jenkins('http://127.0.0.1:8080/', auth=('username', 'password or token'))
    >>> print(j)
    <Jenkins: http://127.0.0.1:8080/>

if Jenkins integrated with LDAP server, sometimes LDAP server will refuse to connect if access with username and password too much often, in  this case, you can set **max_retries(default is 1)** to retry or enable dynamic api token when initialize Jenkins which will create new api token and revoke token when object is destoried by garbage collection.

    >>> j = Jenkins('http://127.0.0.1:8080/', auth=('username', 'password'), token=True)

.. note::

    Any parameter supported by `requests.Session.request <https://requests.readthedocs.io/en/latest/api/#requests.Session.request>`_ can be passed to initialize Jenkins object.

Now, we have a :class:`Jenkins <api4jenkins.Jenkins>` object `j`, let's check if Jenkins exists and retrive its version and crumb value::

    >>> j.exists()
    True
    >>> j.version
    '2.176.2'
    >>> j.crumb
    {'_class': 'hudson.security.csrf.DefaultCrumbIssuer', 'crumb': 'ccc8a8388c8288140361e12526ca8b37aa8b05a33956905976bd57959832a225', 'crumbRequestField': 'Jenkins-Crumb'}

In `api4jenkins <https://github.com/joelee2012/api4jenkins>`_, all classes are inheriented
from class :class:`Item <api4jenkins.item.Item>` which provides many common methods and capability to access any `int, str, bool, none` value of key as attribute(**must be snake case of json key**) of object that returned by requesting `<item url>/api/json`.

For example, we call `j.api_json()` to get data of Jenkins::

    >>> j.api_json()
    {
        "_class": "hudson.model.Hudson",
        "assignedLabels": [
            {
            "name": "master"
            }
        ],
        "mode": "EXCLUSIVE",
        "nodeDescription": "the master Jenkins node",
        "nodeName": "",
        "numExecutors": 1,
        "description": "My Jenkins",
        .....
    }

Then we can access attribute(**must be snake case of json key**) of Jenkins object to get value of key in json::

    # attribute name should be snake case of key in json
    >>> j.description
    'My jenkins'
    >>> j.num_executors
    1
    >>> j.node_description
    'the master Jenkins node

Call `j.dynamic_attrs` to get the dynamic attributes of an Item::

    >>> j.dynamic_attrs
    ['_class', 'mode', 'node_description', 'node_name', 'num_executors', 'description', 'quieting_down', 'slave_agent_port', 'use_crumbs', 'use_security']

With Jenkins object you can manage many Items including: `Job`_, `Credential`_, `Node`_, `View`_, `Queue`_, `Plugin`_, `System`_ and so on. let's start with `Job`_ management.

create job with `j.create_job()`::

    >>> xml = """<?xml version='1.1' encoding='UTF-8'?>
    ... <project>
    ...   <builders>
    ...     <hudson.tasks.Shell>
    ...       <command>echo $JENKINS_VERSION</command>
    ...     </hudson.tasks.Shell>
    ...   </builders>
    ... </project>"""
    >>> j.create_job('freestylejob', xml)

once job is created, we can get it by call `j.get_job()` or by subscript `j['freestylejob']` which will return a :class:`Job <api4jenkins.job.Job>` object::

    >>> job = j.get_job('freestylejob')
    >>> print(job)
    <FreeStyleProject: http://127.0.0.1:8080/job/freestylejob/>

    # optional you can get job by accessing j['freestylejob']
    >>> job = j['freestylejob']

now let's copy a new job and delete new::

    >>> j.copy_job('freestylejob', 'dump-freestylejob')
    >>> dump_job = j.get_job('dump-freestylejob')
    >>> print(dump_job)
    <FreeStyleProject: http://127.0.0.1:8080/job/dump-freestylejob/>
    >>> j.delete_job('dump-freestylejob')
    >>> dump_job = j.get_job('dump-freestylejob')
    >>> print(dump_job)
    None

call `j.build_job()` to trigger job to build if it is buildable, it will return a :class:`QueueItem <api4jenkins.queue.QueueItem>` which can be used for retriving the :class:`Build <api4jenkins.build.Build>`::

    >>> item = j.build_job('freestylejob')
    >>> import time
    >>> while not item.get_build():
    ...      time.sleep(1)
    >>> build = item.get_build()
    >>> print(build)
    <FreeStyleBuild: http://127.0.0.1:8080/job/freestylejob/1/>
    >>> for line in build.progressive_output():
    ...     print(line)

.. note::

    If you don't care console log, you can just poll the building status::

        >>> while build.building:
        ...     time.sleep(1)

    see `Build`_

you can also set delay and `Authentication Token` when trigger build::

    >>> item = j.build_job('freestylejob', delay='30sec', token='abc')

build with parameters is supported too::

    >>> item = j.build_job('freestylejob', arg1='string1', arg2='string2')

it's also possiable to iterate jobs of Jenkins,  iterate jobs in first level::

    # call function straightforward
    >>> for job in j.iter_jobs():
    ...     print(job)

    # or pythonic
    >>> for job in j:
    ...     print(job)

    >>> for job in j(0):
    ...     print(job)

or iterate with depth ::

    >>> for job in j.iter_jobs(3):
    ...     print(job)

    >>> for job in j(3):
    ...     print(job)


use `j.validate_jenkinsfile(content)` to validate your Jenkinsfile,
it returns string '**Jenkinsfile successfully validated.**' if validate successful or error message.::

    >>> j.validate_jenkinsfile('content')


Job
----------------------------------
:class:`Job <api4jenkins.job.Job>` is user configured item in Jenkins, it's the base class of :class:`Folder <api4jenkins.job.Folder>` and its subclass :class:`WorkflowMultiBranchProject <api4jenkins.job.WorkflowMultiBranchProject>`; :class:`Project <api4jenkins.job.Project>` and its subclass
:class:`FreeStyleProject <api4jenkins.job.FreeStyleProject>`, :class:`GitHubSCMNavigator <api4jenkins.job.GitHubSCMNavigator>`, :class:`IvyModuleSet <api4jenkins.job.IvyModuleSet>`, :class:`MatrixProject <api4jenkins.job.MatrixProject>`,
:class:`MavenModuleSet <api4jenkins.job.MavenModuleSet>`, :class:`MultiJobProject <api4jenkins.job.MultiJobProject>`, :class:`WorkflowJob <api4jenkins.job.WorkflowJob>`, :class:`MavenModuleSet <api4jenkins.job.MavenModuleSet>`. as :class:`Job <api4jenkins.job.Job>` is subclass of Item, so we can retrive attributes from json returned by requesting `<Job>/api/json` as well::

    >>> job.api_json()
    {
        "_class": "hudson.model.FreeStyleProject",
        "description": "test job",
        "displayName": "freestylejob",
        "displayNameOrNull": null,
        "fullDisplayName": "freestylejob",
        "fullName": "freestylejob",
        "name": "freestylejob",
        "url": "http://127.0.0.1:8080/job/freestylejob/",
        "buildable": true,
        "builds": [],
        "color": "notbuilt",
        "firstBuild": null,
        "healthReport": [],
        "inQueue": false,
        ...
    }
    >>> job.buildable
    True
    >>> job.display_name
    'freestylejob'

to list all attributes are avaliable in json data

    >>> job.dynamic_attrs
    ['_class', 'description', 'display_name', 'full_display_name', 'full_name', 'name', 'url', 'buildable', 'color', 'in_queue', 'keep_dependencies', 'next_build_number', 'concurrent_build', 'disabled']

get the parent of `Job`

    >>> print(job.parent)

get/update configuration:

    >>> print(job.configure())
    <?xml version='1.1' encoding='UTF-8'?>
    <project>
    ...
    <builders>
        <hudson.tasks.Shell>
        <command>echo $JENKINS_VERSION</command>
        </hudson.tasks.Shell>
    </builders>
    ...
    </project>
    >>> xml = """<?xml version='1.1' encoding='UTF-8'?>
    ... <project>
    ...   <builders>
    ...     <hudson.tasks.Shell>
    ...       <command>echo this is testing!</command>
    ...     </hudson.tasks.Shell>
    ...   </builders>
    ... </project>"""
    >>> job.configure(xml)

.. note::

    method `configure()` is avaliable for Job, View, Credential, Node to get/set the xml configuration.

get/set description of job:

    >>> job.description
    'test job'
    >>> job.set_description('new description')

rename/move/duplicate/delete of itself::

    >>> job.rename('new_name')
    >>> job.move('path/to/new/locathon/')
    >>> job.duplicate('path/to/new/locathon/new_name')
    >>> job.delete()

check if job exists:

    >>> job.exists()
    False


Project
----------------------------------
:class:`Project <api4jenkins.job.Project>` is a kind of **buildable** Item in Jenkins, it's also subclass of Job. besides the methods come from Job, it has following additional methods.

call `Project.build()` will start a :class:`Build <api4jenkins.build.Build>`, it will return a :class:`QueueItem <api4jenkins.queue.QueueItem>` which can be used for retriving build item.

    >>> item = job.build()
    >>> import time
    >>> while not item.get_build():
    ...      time.sleep(1)
    >>> build = item.get_build()
    >>> print(build)
    <FreeStyleBuild: http://127.0.0.1:8080/job/freestylejob/1/>
    >>> for line in build.progressive_output():
    ...     print(line)

build with delay or token

    >>> item = job.build(delay='30sec', token='abc')

build with parameters

    >>> item = job.build(arg1='string1', arg2='string2')

disable/enable project to

    >>> job.disable()
    >>> job.buildable
    False
    >>> job.enable()
    >>> job.buildable
    True

check if any build of project is running

    >>> job.building
    True

get build with given number

    >>> build = job.get_build(1)

or subscript with build number

    >>> build = job[1]

other shortcut methods to get special build:

    >>> job.get_first_build()
    >>> job.get_last_build()
    >>> job.get_last_completed_build()
    >>> job.get_last_failed_build()
    >>> job.get_last_stable_build()
    >>> job.get_last_successful_build()
    >>> job.get_last_unstable_build()
    >>> job.get_last_unsuccessful_build()

set next build number (requires `next-build-number` plugin)

    >>> job.set_next_build_number(1)

iterate all builds of this project, following are same

    >>> for build in job:
    ...     print(build)
    ...
    >>> for build in job.iter_builds():
    ...     print(build)
    ...

see `Build`_


Folder
----------------------------------
:class:`Folder <api4jenkins.job.Folder>` is organizational container in Jenkins, besides methods inheriented from :class:`Job <api4jenkins.job.Job>`, following methods are avaliable:

create empty folder::

    >>> xml = '''<?xml version='1.0' encoding='UTF-8'?>
    ... <com.cloudbees.hudson.plugins.folder.Folder>
    ...  <actions/>
    ...  <description></description>
    ...  <properties/>
    ...  <folderViews/>
    ...  <healthMetrics/>
    ... </com.cloudbees.hudson.plugins.folder.Folder>'''
    >>> j.create_job('folder name', xml)

create new job under the folder:

    >>> xml = """<?xml version='1.1' encoding='UTF-8'?>
    ... <project>
    ...   <builders>
    ...     <hudson.tasks.Shell>
    ...       <command>echo this is testing!</command>
    ...     </hudson.tasks.Shell>
    ...   </builders>
    ... </project>"""
    >>> folder.create('freestylejob', xml)

get one job in the folder::

    >>> job = folder.get('freestylejob')

or with subscript::

    >>> job = folder['freestylejob']

copy job in same folder::

    >>> folder.copy('freestylejob', 'freestylejob2')

reload folder::

    >>> folder.reload()

iterate jobs in folder, set depth for function `Folder.iter()` or obejct `folder` to iterate folder recursively::

    # iter jobs in first level
    >>> for job in folder:
    ...     print(job)
    >>> for job in folder(0):
    ...     print(job)
    >>> for job in folder.iter():
    ...     print(job)

    # iter jobs with depth recursively
    >>> for job in folder(3):
    ...     print(job)

    >>> for job in folder.iter(3):
    ...     print(job)

you can also manage folder based `View`_, `Credential`_

WorkflowMultiBranchProject
--------------------------
WorkflowMultiBranchProject is a kind of `Folder`. it has few dedicated methods, assume you have one WorkflowMultiBranchProject object `branch_project`

    >>> branch_project.scan()
    >>> for line in branch_project.get_scan_log():
    ...     print(line)

Build
-----------------------------------
Build is result of a single execution of a Project, you can get it from :class:`QueueItem <api4jenkins.queue.QueueItem>` or :class:`Project <api4jenkins.job.Project>`

check status and result of build::

    >>> build.building
    True
    # block until build fininsh
    >>> import time
    >>> while build.building:
    ...     time.sleep(2)
    ...
    >>> build.result
    'SUCCESS'


get console output

    >>> for line in build.console_text():
    ...     print(line)
    ...

get progressive output

    >>> for line in build.progressive_output():
    ...     print(line)
    ...

stop/term/kill build, more detail can be found: https://www.jenkins.io/doc/book/using/aborting-a-build/

    >>> build.stop()
    >>> build.term()
    >>> build.kill()

get job of build:

    >>> job = build.get_job()

or get previous/next build:

    >>> pre_build = build.get_previous_build()
    >>> next_build = build.get_next_build()

get/set description of job:

    >>> build.description
    'build 1'
    >>> build.set_description('new description')

delete build

    >>> build.delete()
    >>> build.exists()
    False

Jenkins has plugin `Junit <https://plugins.jenkins.io/junit/>`_ for publishing XML test reports
generated during the builds and provides some graphical visualization of the historical test results.
you can retrieve test reports::

    >>> tr = build.get_test_report()

see `TestReport`_, `TestSuite`_ , `TestCase`_  for more detail

get parameters or causes of build ::

    >>> paramters = build.get_parameters()
    >>> causes = build.get_causes()


WorkflowRun
------------
WorkflowRun is kind of `Build`, more detail to see: https://www.jenkins.io/doc/book/pipeline/

it provides an step `input <https://www.jenkins.io/doc/book/pipeline/syntax/#input>`_ to pause current build until you input something. api4jenkins let you can process it programmatically. assume you have build object which requires two parameters, you can submit as this::

    >>> while not build.get_pending_input():
    ...     time.sleep(1)
    >>> build.get_pending_input().submit(arg1='xyz', arg2=time.asctime())

or if without parameters::

    >>> build.get_pending_input().submit()

and abort input::

    >>> build.get_pending_input().abort()

WorkflowRun supports `archive artfacts <https://www.jenkins.io/doc/pipeline/steps/core/#archiveartifacts-archive-the-artifacts>`_,  you can also process with api4jenkins::

save file you interest::

    >>> for artifacts in build.get_artifacts():
    ...     if artifacts.name == 'you need':
    ...         artfacts.save('filename')

save artifacts as zip::

    >>> build.save_artifacts('filename.zip')


Credential
-------------
Credential is for saving secret data, `api4jenkins` support to manage system and folder based credentials, all credentials must be in default domain(_). more detail can be found: `using credentials <https://www.jenkins.io/doc/book/using/using-credentials/>`_ and `credentials plugin user.doc <https://github.com/jenkinsci/credentials-plugin/blob/master/docs/user.adoc>`_

create/get folder based credential::

    >>> xml = '''<com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
    ...   <id>user-id</id>
    ...   <username>user-name</username>
    ...   <password>user-password</password>
    ...   <description>user id for testing</description>
    ... </com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>'''
    >>> folder.credentials.create(xml)
    >>> credential = folder.credentials.get('user-id')

create system based credential::

    >>> xml = '''<com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
    ...   <scope>GLOBAL</scope>
    ...   <id>user-id</id>
    ...   <username>user-name</username>
    ...   <password>user-password</password>
    ...   <description>user id for testing</description>
    ... </com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>'''
    >>> j.credentials.create(xml)
    >>> credential = j.credentials.get('user-id')

get/update configuration of credential::

    >>> print(credential.configure())
    >>> credential.configure(new_xml)

delete credential::

    >>> credential.delete()
    >>> credential.exists()
    False

iterate folder credentials::

    >>> for c in folder.credentials:
    ...     print(c)

iterate system credentials::

    >>> for c in j.credentials:
    ...     print(c)


View
-------
Views in Jenkins allow us to organize jobs and content into tabbed categories, which are displayed on the main dashboard. `api4jenkins` support to manage system and folder based views

create/get folder based view

    >>> xml = '''<?xml version="1.0" encoding="UTF-8"?>
    ... <hudson.model.ListView>
    ...   <name>EMPTY</name>
    ...   <filterExecutors>false</filterExecutors>
    ...   <filterQueue>false</filterQueue>
    ...   <properties class="hudson.model.View$PropertyList"/>
    ...   <jobNames>
    ...     <comparator class="hudson.util.CaseInsensitiveComparator"/>
    ...   </jobNames>
    ...   <jobFilters/>
    ...   <columns>
    ...     <hudson.views.StatusColumn/>
    ...     <hudson.views.WeatherColumn/>
    ...     <hudson.views.JobColumn/>
    ...     <hudson.views.LastSuccessColumn/>
    ...     <hudson.views.LastFailureColumn/>
    ...     <hudson.views.LastDurationColumn/>
    ...     <hudson.views.BuildButtonColumn/>
    ...   </columns>
    ... </hudson.model.ListView>'''
    >>> folder.views.create('test_view', xml)
    >>> view = folder.views.get('test_view')

create system based view::

    >>> j.views.create('test_view', xml)
    >>> view = j.views.get('test_view')

get/update configuration of view

    >>> print(view.configure())
    >>> view.configure(new_xml)

delete view:

    >>> view.delete()
    >>> view.exists()
    False

iterate views of folder

    >>> for view in folder.views:
    ...     print(view)


get job from view

    >>> job = view.get('job name')

include/exclude job to/from view

    >>> view.include('job name')
    >>> view.exclude('job name')

iterate jobs of view

    >>> for job in view:
    ...     print(job)


Queue
---------
Queue is schedule of executing builds

get queue item by id

    >>> item = j.queue.get('123')

cancel item in queue

    >>> j.queue.cancel('123')

iterate all items in queue

    >>> for item in j.queue:
    ...     print(item)

get job from queue item

    >>> job = item.get_job()

get build from queue item

    >>> build = item.get_build()

get parameters or causes of queue item ::

    >>> paramters = item.get_parameters()
    >>> causes = item.get_causes()

get build from queue item until build is avaliable:

    >>> while not item.get_build():
    ...     time.sleep(1)

cancel item

    >>> item.cancel()
    >>> item.exists()
    False


Plugin
------------
Plugin manager is for managing plugins on Jenkins

get plugin by name

    >>> plugin = j.plugins.get('cloudbees-folder')

install plugin and block until finished, default is unblock

    >>> j.plugins.install('cloudbees-folder', 'credentials', block=True)

uninstall plugins

    >>> j.plugins.uninstall('cloudbees-folder', 'credentials')

set plugin update site

    >>> j.plugins.set_site('url of site')

set proxy for update site

    >>> j.plugins.set_proxy('172.xxx.xx.xxx', '8080')

check update on site

    >>> j.plugins.check_updates_server()

iterate plugins

    >>> for plugin in j.plugins:
    ...     print(plugin)

check if plugin installation is done or restart required

    >>> j.plugins.installation_done
    >>> j.plugins.restart_required

uninstall plugin

    >>> plugin.uninstall()
    >>> plugin.exists()
    False

fully example to install plugins, save following code as install_plugins.py::

    #!python
    URL = 'http://localhost:8080'
    USER = 'admin'
    PASSWORD = '1234'

    def install_plugins(*names):
        import re
        import time
        import os
        from api4jenkins import Jenkins
        jenkins = Jenkins(URL, auth=(USER, PASSWORD))
        if os.getenv('HTTPS_PROXY'):
            matcher = re.match(r'(?P<ip>.*):(?P<port>\d+)$', os.getenv('HTTPS_PROXY'))
            jenkins.plugins.set_proxy(matcher['ip'], port=matcher['port'])
        jenkins.plugins.check_updates_server()
        jenkins.plugins.install(*names, block=True)
        if jenkins.plugins.restart_required:
            jenkins.system.safe_restart()
            while not jenkins.exists():
                time.sleep(2)
        for name in names:
            if not jenkins.plugins.get(name):
                raise RuntimeError(f'{name} was not installed successful')

    if __name__ == '__main__':
        import logging
        import sys
        logging.basicConfig(level=logging.DEBUG)
        install_plugins(*sys.argv[1:])


call install_plugins.py to install plugin::

    python3 install_plugins.py plugin1 plugin2


System
-----------
Perform admin operation,

restart/safe restart/quiet_down/cancel_quiet_down, see `how to start/stop/restart Jenkins <https://support.cloudbees.com/hc/en-us/articles/216118748-How-to-Start-Stop-or-Restart-your-Instance->`_

    >>> j.system.restart()
    >>> j.system.safe_restart()
    >>> j.system.quiet_down()
    >>> j.system.cancel_quiet_down()
    >>> j.system.exit()
    >>> j.system.safe_exit()

run groovy script

    >>> j.system.run_script('println "this is test"')

it also supports to manage `jcasc <https://www.jenkins.io/projects/jcasc/>`_ ::

to reload jcase

    >>> j.system.reload_jcasc()

to download the jcasc, default file name is jenkins.yaml

    >>> j.system.export_jcasc()

to apply new jcasc

    >>> j.system.apply_jcasc('http://host/new_jcasc.yaml')


Node
-------
A machine which is part of the Jenkins environment and capable of executing Pipelines or Projects.

get node

    >>> master = j.nodes.get('master')

create node

    >>> j.nodes.create(**kwargs)

the kwargs must any of :

    >>>
    {
        'nodeDescription': '',
        'numExecutors': 1,
        'remoteFS': '/home/jenkins',
        'labelString': '',
        'mode': 'NORMAL',
        'retentionStrategy': {
            'stapler-class': 'hudson.slaves.RetentionStrategy$Always'
        },
        'nodeProperties': {'stapler-class-bag': 'true'},
        'launcher': {'stapler-class': 'hudson.slaves.JNLPLauncher'}
    }

iterate builds which is executing on nodes

    >>> for build in j.nodes.iter_builds():
    ...     print(build)

iter all building items over jenkins

    >>> for build in j.nodes.iter_builds():
    ...     if build.building:
    ...         print(build)

iterate all nodes:

    >>> for node in j.nodes:
    ...     print(node)

enable/disable node

    >>> node.enable()
    >>> node.disable('set description')

iterate builds which is executing on node

    >>> for build in node.iter_builds():
    ...     print(build)

iter building item over one node

    >>> for build in j.nodes.get('node name'):
    ...     if build.building:
    ...         print(build)

get/update configuration of node

    >>> print(node.configure())
    >>> node.configure(new_xml)

delete node

    >>> node.delete()
    >>> node.exists()
    False

run groovy script on node

    >>> node.run_script('println "this is test"')


User
------
you can manage api token for current user, and set description or delete user

generate/revoke api token for current user, `Jenkins.me` is alias of `Jenkins.user`::

    # j.me.generate_token()
    >>> j.user.generate_token()
    ApiToken(name='Token created on 2020-12-18T09:27:44.209Z', uuid='3d6a2b51-26cd-4788-9395-c218de5e732a', value='11813a7e1abbf8fc78a5bcc82136dc6e28')
    >>> j.user.revoke_token('3d6a2b51-26cd-4788-9395-c218de5e732a')


iterate all known “users”, including login identities which the current security realm can enumerate, as well as people mentioned in commit messages in recorded changelogs.


    >>> for user in j.users:
    ...     print(user)

get user by id or full name ::

    >>> user1 = j.users.get(id='admin')
    >>> user2 = j.user.get(full_name='admin')

set description for user::

    >>> user1.set_description("i'm admin")

delete user:

    >>> user1.delete()


Item
----
An entity in the web UI corresponding to either a: Folder, Pipeline, or Project. Item is base class in api4jenkins. it provides many common methods.

get json/xml data by calling `item.api_json()` or `item.api_xml()`, both of them are support depth and tree, see https://ci.jenkins.io/api/

    >>> item.api_json()
    >>> item.api_xml()

check if item exists

    >>> item.exists()

list and access dynamic attributes(**must be snake case of json key**) come from json data

    >>> item.dynamic_attrs
    >>> item.url

get Jenkins object from item

    >>> j = item.jenkins

customize requests:

    >>> item.handle_req('POST', entry, params=params)


TestReport
----------
Class for test report which was published by `JUnit <https://plugins.jenkins.io/junit/>`_,
you can retrieve from build::

    >>> tr = build.get_test_report()

list dynamic attributes::

    >>> print(tr.dynamic_attrs)

get test suite by name::

    >>> suite = tr.get('name of suite')

iterate each suite of `TestReport`::

    >>> for suite in tr: # same as `for suite in tr.suites`
    ...     print(suite)

show the attributes of `tr`::

    >>> print(tr.dynamic_attrs)

TestSuite
---------
Class for test suite, you can get test case for it::

    >>> case = suite.get('case name')

iterate each test case::

    >>> for case in suite: # same as `for case in suite.cases`
    ...     print(case)


show the attributes of `suite`::

    >>> dir(suite)


TestCase
--------
Class for test case

show the attributes of `case`::

    >>> dir(case)

iterate all case in test report and filter by status ::

    >>> for suite in tr:
    ...     for case in suite:
    ...         if case.status == 'PASSED':
    ...             print(case)