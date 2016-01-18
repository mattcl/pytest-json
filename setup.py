#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-json',
    version='0.4.0',
    author='Matt Chun-Lum',
    author_email='mchunlum@gmail.com',
    maintainer='Matt Chun-Lum',
    maintainer_email='mchunlum@gmail.com',
    license='MIT',
    url='https://github.com/mattcl/pytest-json',
    description='Generate JSON test reports',
    long_description=read('README.rst'),
    packages=['pytest_json'],
    install_requires=['pytest>=2.3'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'json = pytest_json.plugin',
        ],
    },
)
