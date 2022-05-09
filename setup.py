#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, 'api4jenkins', '__version__.py')) as f:
    exec(f.read(), about)

with open('README.md') as f:
    readme = f.read()

requires = [
    'requests >= 2.23.0'
]

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    url=about['__url__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    packages=['api4jenkins'],
    package_data={'': ['LICENSE']},
    python_requires='>=3.6',
    install_requires=requires,
    license=about['__license__'],
    keywords=["RESTAPI", "Jenkins"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development',
    ],
    project_urls={
        'Documentation': about['__documentation__'],
        'Source': about['__url__'],
    },
)
