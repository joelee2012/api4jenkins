.. _install:

Installation
=============

From pypi
----------

The easiest (and best) way to install is through pip::

    $ python -m pip install api4jenkins

From source
-------------------

Optional you can clone the public repository to install::

    $ git clone https://github.com/joelee2012/api4jenkins
    $ cd api4jenkins
    $ python -m pip install .

Prerequisites
------------------
Install following plugins for Jenkins to enable full functionality for api4jenkins:
    - `folder <https://plugins.jenkins.io/cloudbees-folder/>`_
    - `pipeline <https://plugins.jenkins.io/workflow-aggregator/>`_
    - `credentials <https://plugins.jenkins.io/credentials/>`_
    - `next-build-number <https://plugins.jenkins.io/next-build-number/>`_


.. include:: ../../../HISTORY.md