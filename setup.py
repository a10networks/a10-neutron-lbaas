#!/usr/bin/env python
# flake8: noqa

from setuptools import setup, find_packages

setup(
    name = "a10-neutron-lbaas",
    version = "1.5.2",
    packages = find_packages(),

    author = "A10 Networks",
    author_email = "dougw@a10networks.com",
    description = "A10 Networks Openstack LBaaS Driver Middleware",
    license = "Apache",
    keywords = "a10 axapi acos adc slb load balancer openstack neutron lbaas",
    url = "https://github.com/a10networks/a10-neutron-lbaas",

    long_description = open('README.md').read(),

    classifiers = [
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
    ],

    package_data={'': [
        'a10_neutron_lbaas/db/migration/alembic.ini'
    ]},
    include_package_data=True,

    scripts=['scripts/a10-manage', 'scripts/a10-neutron-lbaas-db-manage'],

    install_requires = ['acos-client>=1.3.6', 'a10-openstack-lib>=0.1.0']
)
