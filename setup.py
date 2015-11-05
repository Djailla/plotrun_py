#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Setup py file for plotrunpy project"""

from setuptools import setup

setup(
    name='plotrunpy',
    version='1.0.0',
    description='GPX file analyser to draw custom plot',
    author='Bastien Vallet',
    author_email='bastien.vallet@gmail.com',
    packages=['plotrunpy', ],
    install_requires=[
        'numpy',
        'gpxpy',
        'geopy',
        'pygal',
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    scripts=['gpxinfo']
)
