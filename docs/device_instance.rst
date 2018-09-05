A10 Device Instance Orchestration
================

.. _deviceinstance:

Device Instances
------------

A device instance represents a vThunder that has been instantiated as an Openstack Nova server utilizing a specified image, flavor, networks, and device configuration.

.. _deviceinstance-datafields:

Device Instance Data Fields
^^^^^^^^^^^^^^^^^^^^^^^

``name``
    Name of the created vThunder device instance

``description``
    User-specified description of instance

``username``
    Username for AXAPI authentication

``password``
    Password for AXAPI authentication

``api_version``
    AXAPI version (2.1 for ACOS 2.7.x, 3.0 for ACOS 4.x)

``protocol``
    Protocol to use when interacting with AXAPI (HTTP or HTTPS)

``port``
    TCP port to use when interacting with AXAPI (80 for HTTP, 443 for HTTPS)

``networks``
    Ordered list of Neutron network names or IDs to attach to vThunder. Management network is 1st element in the list.

``image``
    ID or name of Nova/Glance image to use for vThunder instance

``flavor``
    ID or name of Nova flavor for vThunder instance

