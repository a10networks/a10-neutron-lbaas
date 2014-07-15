#!/usr/bin/env python

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "a10-neutron-lbaas",
    version = "0.1",
    packages = ['a10_neutron_lbaas'],

    data_files = []

    author = "A10 Networks",
    author_email = "dougw@a10networks.com",
    description = "A10 Networks Openstack LBaaS Driver, Juno",
    license = "Apache",
    keywords = "a10 axapi acos adc slb load balancer",
    url = "https://github.com/a10networks/a10-neutron-lbaas",

    long_description = read('README.md'),

    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
    ],

    install_requires = ['acos-client>=0.4']
)
