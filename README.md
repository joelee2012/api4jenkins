[![Unit Test](https://github.com/joelee2012/api4jenkins/actions/workflows/unittest.yml/badge.svg?branch=main)](https://github.com/joelee2012/api4jenkins/actions/workflows/unittest.yml)
[![Integration Test](https://github.com/joelee2012/api4jenkins/actions/workflows/integration.yml/badge.svg?branch=main)](https://github.com/joelee2012/api4jenkins/actions/workflows/integration.yml)
![CodeQL](https://github.com/joelee2012/api4jenkins/workflows/CodeQL/badge.svg?branch=main)
[![codecov](https://codecov.io/gh/joelee2012/api4jenkins/branch/main/graph/badge.svg?token=YGM4CIB149)](https://codecov.io/gh/joelee2012/api4jenkins)
![PyPI](https://img.shields.io/pypi/v/api4jenkins)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/api4jenkins)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/api4jenkins)
[![Documentation Status](https://readthedocs.org/projects/api4jenkins/badge/?version=latest)](https://api4jenkins.readthedocs.io/en/latest/?badge=latest)
![GitHub](https://img.shields.io/github/license/joelee2012/api4jenkins)


# Jenkins Python Client

[Python3](https://www.python.org/) client library for [Jenkins API](https://www.jenkins.io/doc/book/using/remote-access-api/) which provides sync and async APIs.

# Features

- Provides sync and async APIs
- Object oriented, each Jenkins item has corresponding class, easy to use and extend
- Base on `api/json`, easy to query/filter attribute of item
- Setup relationship between class just like Jenkins item
- Support api for almost every Jenkins item
- Pythonic
- Test with latest Jenkins LTS

# Installation

```bash
python3 -m pip install api4jenkins
```

# Quick start

Sync example:

```python
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
```

Async example

```python
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
```

# Documentation
User Guide and API Reference is available on [Read the Docs](https://api4jenkins.readthedocs.io/)

