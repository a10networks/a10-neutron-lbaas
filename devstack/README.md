A10 Networks devstack plugin
============================

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

    enable_plugin neutron-lbaas https://git.openstack.org/openstack/neutron-lbaas master
    enable_plugin a10networks https://github.com/a10networks/a10-neutron-lbaas.git master

2a) To enable LBaaS version 2 with the A10 Networks driver:

    ENABLED_SERVICES+=q-lbaasv2,a10-lbaasv2

2b) To enable LBaaS version 1 with the A10 Networks driver:

    ENABLED_SERVICES+=q-lbaas,a10-lbaasv1

For more information, see the "Externally Hosted Plugins" section of
http://docs.openstack.org/developer/devstack/plugins.html.

Sample local.conf, lbaasv2, vxlan, single nic
=============================================

```
[[local|localrc]] LOGFILE=stack.sh.log
LOGFILE=stack.sh.log
SCREEN_LOGDIR=/opt/stack/data/log
LOG_COLOR=False
#OFFLINE=True
RECLONE=yes

disable_service swift
disable_service cinder
disable_service n-net
enable_service q-svc
enable_service q-dhcp
enable_service q-l3
enable_service q-meta
enable_service q-metering
enable_service neutron
enable_service q-lbaasv2
enable_service a10-lbaasv2
A10_DEVICE_HOST=10.48.7.86

# NOTE: Set this to your hosts IP
HOST_IP=$(ip a | grep eth0 | grep inet | awk '{print $2}' | cut -f1 -d/)

Q_PLUGIN=ml2
Q_ML2_PLUGIN_MECHANISM_DRIVERS=openvswitch,logger
Q_AGENT=openvswitch
enable_service q-agt
ENABLE_TENANT_TUNNELS=True

Q_ML2_TENANT_NETWORK_TYPE=vxlan
Q_ML2_PLUGIN_TYPE_DRIVERS=vxlan
Q_ML2_PLUGIN_VXLAN_TYPE_OPTIONS=(vni_ranges=1001:2000)
Q_AGENT_EXTRA_AGENT_OPTS=(tunnel_types=vxlan vxlan_udp_port=8472)
Q_USE_NAMESPACE=True
Q_USE_SECGROUP=True

# The below is needed on Fedora/CentOS
#disable_service rabbit
#enable_service qpid

HOST_NAME=$(hostname)
SERVICE_HOST_NAME=${HOST_NAME}
# NOTE: Set this to your HOST IP
SERVICE_HOST=$HOST_IP

# NOTE: Set this to your HOST IP
VNCSERVER_PROXYCLIENT_ADDRESS=$HOST_IP
VNCSERVER_LISTEN=0.0.0.0

#FLOATING_RANGE=192.168.100.0/24
MYSQL_HOST=$SERVICE_HOST
RABBIT_HOST=$SERVICE_HOST
GLANCE_HOSTPORT=$SERVICE_HOST:9292
KEYSTONE_AUTH_HOST=$SERVICE_HOST
KEYSTONE_SERVICE_HOST=$SERVICE_HOST

MYSQL_PASSWORD=mysql
RABBIT_PASSWORD=rabbit
SERVICE_TOKEN=service
SERVICE_PASSWORD=admin
ADMIN_PASSWORD=admin
```