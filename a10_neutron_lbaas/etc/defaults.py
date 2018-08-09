#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# Please refer to a10_neutron_lbaas.etc.config for documentation
# about these settings.

import a10_neutron_lbaas.plumbing_hooks


GLOBAL_DEFAULTS = {
    "verify_appliances": False,
    "use_database": True,
    "database_connection": None,
    "neutron_conf_dir": '/etc/neutron',
    "member_name_use_uuid": False,
    "keystone_auth_url": None,
    "keystone_version": 2,
    "plumbing_hooks_class": a10_neutron_lbaas.plumbing_hooks.PlumbingHooks,
    "nova_api_version": "2.1",
    "vport_defaults": {},
}

DEVICE_REQUIRED_FIELDS = [
    "host",
    "username",
    "password",
    "api_version",
]

DEVICE_OPTIONAL_DEFAULTS = {
    "protocol": "https",
    "port": 443,
    "autosnat": False,
    "conn_limit": 8000000,
    "default_virtual_server_vrid": None,
    "ha_sync_list": [],
    "ipinip": False,
    "source_nat_pool": None,
    "shared_partition": "shared",
    "status": True,
    "use_float": False,
    "vport_defaults": {},
    "v_method": "LSI",
    "write_memory": True,
    # "max_instance": 5000,
    # "method": "hash",

    # "max_partitions": 10,
    # "per_partition_lif_max": 10,
    # "peer_mgmt_ip": "",
    # "peer_mgmt_port": "",
    # "vlan": 0,
    # "gateway_mode": 1,
}

VTHUNDER_REQUIRED_FIELDS = [
    'username',
    'password',

    'nova_flavor',
    'glance_image',

    'vthunder_management_network',
    'vthunder_data_networks',
]

VTHUNDER_OPTIONAL_DEFAULTS = DEVICE_OPTIONAL_DEFAULTS
VTHUNDER_OPTIONAL_DEFAULTS = dict(DEVICE_OPTIONAL_DEFAULTS)
VTHUNDER_OPTIONAL_DEFAULTS.update({
    'autosnat': True,
    'v_method': 'LSI',
    'api_version': '3.0',
})
