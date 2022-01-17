![Tests](https://github.com/joelee2012/api4jenkins/workflows/Tests/badge.svg?branch=master)
![CodeQL](https://github.com/joelee2012/api4jenkins/workflows/CodeQL/badge.svg?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/joelee2012/api4jenkins/badge.svg?branch=master)](https://coveralls.io/github/joelee2012/api4jenkins?branch=master)
[![codecov](https://codecov.io/gh/joelee2012/api4jenkins/branch/master/graph/badge.svg?token=YGM4CIB149)](https://codecov.io/gh/joelee2012/api4jenkins)
![PyPI](https://img.shields.io/pypi/v/api4jenkins)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/api4jenkins)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/api4jenkins)
[![Documentation Status](https://readthedocs.org/projects/api4jenkins/badge/?version=latest)](https://api4jenkins.readthedocs.io/en/latest/?badge=latest)
![GitHub](https://img.shields.io/github/license/joelee2012/api4jenkins)


# Jenkins Python Client

[Python3](https://www.python.org/) client library for [Jenkins API](https://wiki.jenkins.io/display/JENKINS/Remote+access+API).

# Features

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

```python
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
>>> import time
>>> item = j.build_job('freestylejob')
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

# Documentation
User Guide and API Reference is available on [Read the Docs](https://api4jenkins.readthedocs.io/)

