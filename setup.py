#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


REQUIRES = [
    'django>=1.9',
    'django-infinite-scroll-pagination>=0.1.3',
    'gcoin>=1.0'
    'gcoinrpc>=0.4',
    'mock',
    'MySQL-python>=1.2.5',
    'tornado>=4.4.1',
]

setup(
    name='diqi_oss',
    description='DiQi OSS',
    author='DiQi',
    keywords='gcoin',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=REQUIRES,
    package_data={
        '': ['*.blk']
    }
)
