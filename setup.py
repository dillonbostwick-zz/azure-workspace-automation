#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='Distutils',
      version='0.1',
      description='Auto-deply an Azure Databricks workspace',
      author='Dillon Bostwick',
      author_email='sales@databricks.com',
      url='',
      packages=find_packages(),
      install_requires=[
	'azure',
      	'requests',
      	'databricks-cli',
      	'adal',
      	'selenium',
        'msrestazure'
      ],
)
