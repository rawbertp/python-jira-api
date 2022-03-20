#!/usr/bin/env python

from distutils.core import setup

setup(name='jira-api-wrapper',
      version='1.0',
      description='Python JIRA API Wrapper',
      author='Robert Porisenko',
      author_email='robert.porisenko@bearingpoint.com',
      url='https://github.com/rawbertp/python-jira-api',
      packages=['jirawrapper'],
      install_requires=["atlassian-python-api>=3.20.1"],
     )
