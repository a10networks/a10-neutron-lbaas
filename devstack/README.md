This directory contains the A10 Networks LBaaS driver devstack plugin.
To use it, you will need to make two modifications to the [[local|localrc]]
section of your local.conf file.

1) Enable the plugin

To enable the plugin, add a line of the form:

    enable_plugin a10networks <GITURL> [GITREF]

where

    <GITURL> is the URL of an a10networks lbaas repository
    [GITREF] is an optional git ref (branch/ref/tag).  The default is
             master.

For example

    enable_plugin a10networks https://github.com/a10networks/a10-neutron-lbaas.git master

2a) To enable LBaaS version 2 with the A10 Networks driver:

    ENABLED_SERVICES+=q-lbaasv2,a10-lbaasv2

2b) To enable LBaaS version 1 with the A10 Networks driver:

    ENABLED_SERVICES+=q-lbaas,a10-lbaasv1

For more information, see the "Externally Hosted Plugins" section of
http://docs.openstack.org/developer/devstack/plugins.html.
