# A10 Networks Openstack LBaaS v1/v2 Driver
===========================================

A10 Networks LBaaS Driver for Thunder, vThunder and AX Series Appliances

Supported releases:

* OpenStack: Liberty - Queens Releases
* LBaaS versions: v2
* ACOS versions: ACOS 2/AxAPI 2.1 (ACOS 2.7.2+), ACOS 4/AxAPI 3.0 (ACOS 4.0.1-GA +)

Working but not available for support:

* OpenStack: git/master

Unsupported, but may work with minor tweaking:

* OpenStack: v1 on any release, v2 Havana through Kilo

## A10 github repos

- [a10-neutron-lbaas](https://github.com/a10networks/a10-neutron-lbaas) - Main A10 LBaaS driver repo. Middleware sitting between the
openstack driver and our API client, mapping openstack constructs to A10's AxAPI.
- [acos-client](https://github.com/a10networks/acos-client) - AxAPI client used by A10's OpenStack driver
- [a10-openstack-lbaas](https://github.com/a10networks/a10-openstack-lbaas) - OpenStack LBaaS driver,
identical to the files that are currently merged into neutron-lbaas.  Pypi package
'a10-openstack-lbaas'.
- [a10-openstack-lbaas, havana branch](https://github.com/a10networks/a10-openstack-lbaas/tree/havana) - OpenStack
LBaaS driver, for the Havana release.  Pypi package 'a10-openstack-lbaas-havana'.
- [a10networks-ci/project-config](https://github.com/a10networks-ci/project-config) - A10 Networks OpenStack third-party CI setup scripts

## Implementation:

![image2](https://cloud.githubusercontent.com/assets/1424573/2849597/47192238-d0df-11e3-9e1e-9e234be58412.png)

## Installation steps:

### Step 1:

Make sure you have neutron installed, and neutron-lbaas if applicable. This
driver will need to be installed on all of your neutron controller nodes
(anywhere that neutron-server is running.)

### Step 2:

The latest supported version of a10-neutron-lbaas is available via standard pypi repositories and the current development version is available on github.

#### Installation from pypi
```sh
sudo pip install a10-neutron-lbaas
```

#### Installation from cloned git repository.

Download the driver from: <https://github.com/a10networks/a10-neutron-lbaas>

![screen shot 2016-03-22 at 4 41 04 pm](https://cloud.githubusercontent.com/assets/603553/13970211/ee35777c-f04c-11e5-9cd2-7c4dd8a66a3a.png)

```sh
sudo pip install git+https://github.com/a10networks/a10-neutron-lbaas.git
```

```sh
git clone https://github.com/a10networks/a10-neutron-lbaas.git
cd a10-neutron-lbaas
sudo pip install -e .
```

## Configuration

Post-installation configuration requires modification of your neutron.conf or neutron_lbaas.conf (neutron_lbaas.conf is only present in LBaaSv2) typically located in `/etc/neutron`.

### LBaaS v1 configuration
Open `/etc/neutron/neutron.conf` in your preferred text editor.
Under the `service_plugins` setting, ensure `lbaas` or `lbaasv2` is listed depending on your configuration.

In the list of `service_provider` settings, add a service provider for A10
Networks:
`service_provider = LOADBALANCER:A10Networks:neutron_lbaas.services.loadbalancer.drivers.a10networks.driver_v1.ThunderDriver:default`

Save and close neutron.conf

### LBaaS v2 configuration
Open `/etc/neutron/neutron.conf` in your preferred text editor.
Under the `service_plugins` setting, ensure `lbaasv2` is listed.
Save and close neutron.conf.

Open `/etc/neutron/neutron_lbaas.conf` in your preferred text editor.

In the list of `service_provider` settings, add a service provider for A10
Networks:
`service_provider = LOADBALANCERV2:A10Networks:neutron_lbaas.drivers.a10networks.driver_v2.ThunderDriver:default`

#### Extension configuration
Open `/etc/neutron/neutron.conf` in your preferred text editor.
Under the `service_plugins` setting, ensure `a10_neutron_lbaas.neutron_ext.services.a10_device_instance.plugin.A10DeviceInstancePlugin` is listed. The `service_plugins` are separated by `,`s.

Under the `api_extensions_path` setting, ensure the path to `a10_neutron_lbaas.neutron_ext.extensions` is listed. The `api_extensions_path`s are separated by `:`s. You can find the path of the installed extension by running 
```shell
python -c "import os; import a10_neutron_lbaas.neutron_ext.extensions as m; print(os.path.dirname(os.path.abspath(m.__file__)))"`.
```

## Creating A10 Devices

### A10 Device configuration
A10 devices are stored in the neutron database and can be created using the neutron cli.

The following command configures an A10 device in the neutron database with a name of `ax1` that can be reached by accessing `10.10.100.20`, using a username of `admin`, a password of `a10`, and AXAPI version `3.0`.  All server load balancers will be configured with `autosnat` enabled, using the `http` protocol and using port `80`.
```shell
neutron a10-device-create 10.10.100.20 admin a10 3.0 --a10-opts autosnat,protocol=http,port=80 --name ax1
```

##### `host` (required)

The ip address or host name of the A10 appliance. For a virtual chassis configuration, this should be the floating host or ip address of the master.

##### `username` and `password` (required)

Authentication credentials to control the A10 appliance via the AXAPI.

##### `api version` (required)

The AXAPI version utilized to access Thunder devices and vThunder applicances.  This is dependent on your image version:

* ACOS version 2.x - `"2.1"`
* ACOS version 4.x - `"3.0"`
`
##### `port` (default `443`)

Port that the AXAPI is exposed on

##### `protocol` (default `http`)

Port that the AXAPI is using.

`http` or `https`

#### A10 Optional Parameters `--a10-opts`
Various ACOS settings can be set for the a10-device.  These settings will be applied to all server load balancers that are created on the a10-device.  Specifying `--a10-opts` is optional, and the defaults will be taken if none are specified.

Pass a comma or space separated list of options to `--a10-opts`

To enable a boolean options, simply supply it in the list of options.

To disable a boolean option, prefix `no-` to the option.  For example to disable `write-memory`, pass `no-write-memory` in the `--a10-opts` list.

Prefix `no-` to options with assigned values to null out the value in the database.  For example `no-default-virtual-server-vrid` will make it's value null.

Note: When updating options, it will be necessary to recreate existing Load Balancers and VIPs for the config options to be passed to the A10 device or vThunder. 

##### `autosnat` (default `False`)

Source address translation is configured on the VIP.

##### `conn-limit` (default `8000000`)

Specify the maximum number of concurrent connections allowed on a real server.

##### `default-virtual-server-vrid` (default `None`)

Virtual servers will be created on this VRID. The VRID must already be configured on the device. Example values: None, 1, 2, ...

##### `ha-sync-list` (defalut `False`)

Contains a list of hostnames or IP addresses that the driver will run the `ha sync` command against whenever a write operation occurs.

##### `ipinip` (defalut `False`)

Enable IP in IP on vports.

##### `source-nat-pool` (default `None`)

Set to the name of a nat pool to use that pool for source nat on vports the nat pool must already exist on the ACOS device.

##### `shared-partition` (default `shared`)

If using a shared partition (v_method=LSI), then this field configures which partition to use. By default, it is the main shared partition.

##### `use-float` (default `False`)

Utilize the floating address of the member and not the actual interface ip.

For nova based pool/service-group members, setting this to True will cause the driver to lookup the nova server's floating ip and use that for communication instead of its neutron port IP address.

##### `v-method` (default `LSI`)

Partition method; "LSI" to put all slb's in a single shared partition, or "ADP" to use a partition per tenant. Partitions are RBA style in ACOS 2.x, and L3V in ACOS 4.x.

* LSI (Logical Service Instance) This configuration is realized by multiple tenant VIPs in the shared partition.

* ADP (Application Delivery Partition) This refers to the RBAC partitions on the Advanced Core Operating System
(ACOS) on any Thunder/AX device.

##### `write-memory` (default `True`)

Enable or disable calling write memory directly after any operation that changes ACOS's running state. Turning this off also disables all ha sync operations, regardless of the settings in ha_sync_list.


### vThunder Appliance Configuration

A10's LBaaS driver supports a default scheduling strategy of "one appliance per tenant".  Create vThunder configuarations using the neutron cli.

neutron a10-vthunder-create `nova-flavor` `glance-image` `username` `api-version` `vthunder-management-network` `[vthunder-data-neteworks]` 
```shell
neutron a10-vthunder-create acos.min c2722746-0c06-48b1-93c3-a9dbc2f6e628 admin a10 3.0 private vipnet,membernet --a10-opts vthunder-tenant-name=admina,vthunder-tenant-username=admina,vthunder-tenant-password=password
```

##### `username` (required)

The administrator username on your vThunder appliance image.

##### `password` (required)

The administrator password on your vThunder appliance image.

##### `api-version` (required)

The AXAPI version utilized to access vThunder appliances.  This is dependent on your vThunder appliance image version:

* 2.7.x - `"2.1"`
* 4.x.x - `"3.0"`

##### `nova-flavor` (required)

The name of the nova flavor used to construct vThunder device instances.  The minimum requirements are dependent on your vThunder appliance image version:

##### 2.7.x
* CPU: 1 VCPU
* RAM: 2GB
* Storage: 12GB

##### 4.x.x
* CPU: 1 VCPU
* RAM: 4GB
* Storage: 12GB

##### `glance-image` (required)

The Glance or Nova image ID of your vThunder appliance image.  This can be obtained through Horizon or the Openstack CLI.

##### `vthunder-tenant-name` (required)

The name of the service tenant where vThunder appliance instances will be created.

##### `vthunder-tenant-username` (required)

The Openstack user login name which has access to the above-named service tenant.

##### `vthunder-tenant-passsword` (required)

The Openstack password of the above-mentioned login.

##### `vthunder-management-networks` (required)

The Openstack network name or ID that the vThunder management interface will be connected to.

##### `vthunder-data-networks` (required)

A list of Openstack network names or IDs that the vThunder data interfaces will be connected to.  A minimum of one is required.

##### `port` (default `443`)

Port that the AXAPI is exposed on

##### `protocol` (default `http`)

Port that the AXAPI is using.

`http` or `https`

### A10 config.py 
A10 devices and vThunder configurations are now managed using the neutron cli.  All other config options are managed in the `/etc/a10/config.py` config file.

For complete documentation of the a10 config.py file, please refer to the [sample config file](https://github.com/a10networks/a10-neutron-lbaas/blob/master/a10_neutron_lbaas/etc/config.py).

### Essential device configuration

##### `host` (required)

The ip address or host name of the A10 appliance. For a virtual chassis configuration, this should be the floating host or ip address of the master.

##### `port` (default `443`)

Port that the AXAPI is exposed on

##### `username` and `password` (required)

Authentication credentials to control the A10 appliance via the AXAPI.

##### `api-version` (default `"2.1"`)

Version of the A10 appliance's AXAPI. `"2.1"` for 2.X series ACOS versions,
`"3.0"` for 4.X versions.


### vThunder License Manager Configuration
The A10 vThunder virtual load balancing appliance has a flexible system for licensing.  Below is a sample configuration for license management (stored in `/etc/a10/config.py`):
```python
license_manager = {
        "hosts": [
                {"ip": "pdx.a10cloud.com", "port": 443},
                {"ip": "sfo.a10cloud.com", "port": 443},
                {"ip": "iad.a10cloud.com", "port": 443}
        ],
        "serial": "SN0123456789ABCDEF",
        "instance-name": "SCALING_INSTANCE",
        "bandwidth-base": 100,
        "interval": 3,
        "use-mgmt-port": True
}
```

#### `hosts` (required)
A list of host entries specifying the IP address or hostname and TCP port of licensing servers.

#### `serial` (required)
The serial number used for your vThunder appliances

#### `instance-name` (required)
The instance name attached to the license.

#### `bandwidth-base` (required for Pay-As-You-Go licensing)
The feature's bandwidth base measured in megabytes.

#### `interval` (required for Pay-As-You-Go licensing)
The feature's bandwidth allowance interval.
* 1 - Monthly
* 2 - Daily
* 3 - Hourly

#### `use-mgmt-port`
The appliance will use the management port for communicating with the licensing server if set to True.  By default, the appliance will use the use the first available interface for license server operations.

More details about A10 Licensing can be found at `TODO(Add licensing info url)`.

## Install database migrations

If 'use_database' is enabled, after installing the package and after any
upgrades, run:

```
a10-manage upgrade
```

## Restart necessary services

Restart neutron after configuration updates in the /etc/a10/config.py file (exact command may vary depending on OpenStack packaging.)

```sh
service neutron-server restart
```

Note: it is no longer necessary to restart neutron when adding, updating or deleting a10-devices or a10-vthunders using the neutron cli.

## Example architectures

You must configure the network elements of the Thunder appliance for OpenStack.

### SNAT:

![image3](https://cloud.githubusercontent.com/assets/1424573/2849593/4708b7ea-d0df-11e3-8ed7-f6bf73b31535.png)

### VLAN:

![image4](https://cloud.githubusercontent.com/assets/1424573/2849595/471863d4-d0df-11e3-87c7-2423aaaaedca.png)


## Verifying installation (lbaas v1)

### Step 1:

Login to the OpenStack dashboard.

![image7](https://cloud.githubusercontent.com/assets/1424573/2849592/46f86d4a-d0df-11e3-8b57-25d2d796f1cc.png)

### Step 2:

Under the “Network” menu, go to the “Load Balancers” tab and select “Add Pool”:

![image8](https://cloud.githubusercontent.com/assets/1424573/2849594/47169bda-d0df-11e3-9fda-af2da76cdb00.png)

Once you have added a pool, a success message should appear.

![image9](https://cloud.githubusercontent.com/assets/1424573/2849599/471a7c14-d0df-11e3-918e-778dbea9be45.png)

### Step 3:

Login to the GUI on your Thunder or AX device, and validate which configuration was applied if the ADPs are set. The ADP name is the first 13 characters of the tenant ID.

![image10](https://cloud.githubusercontent.com/assets/1424573/2849596/4718b0b4-d0df-11e3-9a6b-506bb832dcce.png)

_Repeat this for all configuration steps, then delete all resources if ADPs are configured. They should be deleted when the tenant has no more resources configured._

## Default and Name-based configuration
See [name-based config example](https://github.com/a10networks/a10-neutron-lbaas/tree/master/a10_neutron_lbaas/etc) for details.

## Changes
See [CHANGELOG](https://github.com/a10networks/a10-neutron-lbaas/tree/master/CHANGELOG) for changes made. NOTE: We didn't have a changelog until 1.6.5

## A10 Community

Feel free to fork, submit pull requests, or join us on freenode IRC, channel #a10-openstack. Serious support escalations and formal feature requests must
still go through standard A10 processes.

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request
