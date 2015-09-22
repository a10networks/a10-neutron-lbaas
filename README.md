# A10 Networks Openstack LBaaS v1/v2 Driver
=================

A10 Networks, Openstack Neutron LBaaS Driver for Juno

This package enables LBaaS v1/v2 support for A10 appliances.

A10 github repos:

- [a10-openstack-lbaas](https://github.com/a10networks/a10-openstack-lbaas) - OpenStack LBaaS driver, 
identical to the files that are currently merged into Juno.  Also supports Icehouse.  Pypi package 
'a10-openstack-lbaas'.
- [a10-openstack-lbaas, havana branch](https://github.com/a10networks/a10-openstack-lbaas/tree/havana) - OpenStack 
LBaaS driver, for the Havana release.  Pypi package 'a10-openstack-lbaas-havana'.
- [a10-neutron-lbaas](https://github.com/a10networks/a10-neutron-lbaas) - Middleware sitting between the 
openstack driver and our API client, mapping openstack constructs to A10's AxAPI.
- [acos-client](https://github.com/a10networks/acos-client) - AxAPI client used by A10's OpenStack driver.
- [neutron-thirdparty-ci](https://github.com/a10networks/neutron-thirdparty-ci) - Scripts used by 
our Jenkins/Zuul/Devstack-Gate setup, used to test every openstack code review submission against 
A10 appliances and our drivers.

## Installation

Installation of A10's LBaaS implementation for Neutron is simple.  Install, configure, and restart affected services.  The latest release version of a10-neutron-lbaas is available via standard pypi repositories and the current development version is available here.

##### Installation from pypi
```sh
sudo pip install a10-neutron-lbaas
```

##### Installation from cloned git repository.
```sh
git clone https://github.com/a10networks/a10-neutron-lbaas.git
cd a10-neutron-lbaas
sudo pip install -e .
```


## Configuration

Post-installation configuration requires modification of your neutron.conf or neutron_lbaas.conf (neutron_lbaas.conf is only present in LBaaSv2) typically located in `/etc/neutron`.

##### LBaaS v1 configuration
Open `/etc/neutron/neutron.conf` in your preferred text editor.
Under the `service_plugins` setting, ensure `neutron.services.loadbalancer.plugin.LoadBalancerPlugin` is listed.

In the list of `service_provider` settings, ensure there is only a single entry for LOADBALANCER (you can comment out existing entries) enabled:
`service_provider = LOADBALANCER:A10Networks:neutron_lbaas.services.loadbalancer.drivers.a10networks.driver_v1.ThunderDriver:default`

Save and close neutron.conf

##### LBaaS v2 configuration
Open `/etc/neutron/neutron.conf` in your preferred text editor.
Under the `service_plugins` setting, ensure `neutron_lbaas.services.loadbalancer.plugin.LoadBalancerPluginv2` is listed.
Save and close neutron.conf.

Open `/etc/neutron/neutron_lbaas.conf` in your preferred text editor.

In the list of `service_provider` settings, ensure there is only a single entry for LOADBALANCERV2 (you can comment out existing entries) enabled:
`service_provider = LOADBALANCERV2:A10Networks:neutron_lbaas.drivers.a10networks.driver_v2.ThunderDriver:default`

##### Device configuration

After installation, you will need to provide configuration for the driver so the driver is aware of the appliances you have configured.  The configuration is a standard JSON structure stored in `/etc/a10/config.py`.  Below is a sample to show options and formatting:
```python
devices = {
    "ax1": {
        "name": "ax1",
        "host": "10.10.100.20",
        "port": 443,
        "username": "admin",
        "password": "a10",
        "status": True,
        "default_virtual_server_vrid": 1,
        "autosnat": False,
        "api_version": "3.0",
        "v_method": "ADP",
        "max_instance": 5000,
        "use_float": False,
        "method": "hash",
        "max_partitions": 10,
        "per_partition_lif_max": 10,
        "peer_mgmt_ip": "",
        "peer_mgmt_port": "",
        "vlan": 0,
        "gateway_mode": 1,
        ],
    },
    "ax4": {
        "host": "10.10.100.23",
        "username": "admin",
        "password": "a10",
    },
}
```

## Restart necessary services
Restart the `q-svc` and `q-lbaas2` services after configuration updates.
