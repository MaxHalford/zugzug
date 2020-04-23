#!/usr/bin/env python3

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='zugzug',
    version='0.0.1',
    author='Max Halford',
    license='MIT',
    author_email='maxhalford25@gmail.com',
    description='Monte Carlo experiments for Hearthstone',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/MaxHalford/zugzug',
    packages=['zugzug'],
    install_requires=['tabulate', 'tqdm'],
    extras_require={'dev': ['mypy', 'pytest']},
    python_requires='>=3.6'
)

