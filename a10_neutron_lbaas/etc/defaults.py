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

GLOBAL_DEFAULTS = {
    "verify_appliances": False,
    "use_database": False,
    "database_connection": None,
    "neutron_conf_dir": '/etc/neutron',
}

DEVICE_REQUIRED_FIELDS = [
    "host",
    "username",
    "password",
]

DEVICE_OPTIONAL_DEFAULTS = {
    "protocol": "https",
    "port": 443,
    "api_version": "2.1",
    "status": True,
    "autosnat": False,
    "v_method": "LSI",
    "shared_partition": "shared",
    "use_float": False,
    "default_virtual_server_vrid": None,
    "ipinip": False,
    "ha_sync_list": [],
    "write_memory": True,

    # "max_instance": 5000,
    # "method": "hash",

    # "max_partitions": 10,
    # "per_partition_lif_max": 10,
    # "peer_mgmt_ip": "",
    # "peer_mgmt_port": "",
    # "default_virtual_server_vrid": 1,
    # "vlan": 0,
    # "gateway_mode": 1,
}
