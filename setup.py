#!/usr/bin/env python

from distutils.core import setup

setup(name='Distutils',
      version='0.1',
      description='Auto-deply an Azure Databricks workspace',
      author='Dillon Bostwick',
      author_email='sales@databricks.com',
      url='',
      packages=[
      	'azure',
      	'requests',
      	'databricks-cli',
      	'adal',
      	'selenium',
      	'chromedriver_installer'
      ],
)