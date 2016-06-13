# Copyright 2014, Doug Wiegley (dougwig), A10 Networks
#
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

verify_appliances = True

devices = {
    "ax1": {
        "name": "ax1",
        "host": "10.10.100.20",
        "port": 8443,
        "protocol": "https",
        "username": "admin",
        "password": "a10",
        "status": True,
        "autosnat": True,
        "api_version": "2.1",
        "v_method": "LSI",
        "max_instance": 5000,
        "use_float": True,
        "method": "hash"
    },
    "ax2": {
        "name": "ax2",
        "host": "10.10.100.21",
        "port": 8080,
        "protocol": "http",
        "username": "admin",
        "password": "a10",
        "status": False,
        "api_version": "2.1",
        "v_method": "LSI",
        "max_instance": 5000,
        "use_float": True,
        "method": "hash"
    },
    "ax3": {
        "host": "10.10.100.22",
        "protocol": "http",
        "username": "admin",
        "password": "a10",
        "status": True,
        "api_version": "2.1",
        "max_instance": 5000,
        "use_float": True,
    },
    "ax4": {
        "host": "10.10.100.23",
        "username": "admin",
        "password": "a10",
        "api_version": "2.1",
        "use_float": True,
        "ha_sync_list": [
            {
                "name": "ax5",
                "ip": "1.1.1.1",
                "username": "admin",
                "password": "a10"
            }
        ]
    },
    "axxv21": {
        "host": "10.10.100.29",
        "protocol": "http",
        "username": "admin",
        "password": "a10",
        "status": True,
        "api_version": "2.1",
        "max_instance": 5000,
        "use_float": True,
    },
    "axv30": {
        "host": "10.10.100.30",
        "protocol": "http",
        "username": "admin",
        "password": "a10",
        "status": True,
        "api_version": "3.0",
        "max_instance": 5000,
        "use_float": True,
    },
    # "axadp": {
    #     "host": "10.10.100.24",
    #     "username": "admin",
    #     "password": "a10",
    #     "protocol": "https",
    #     "v_method": "ADP",
    # },
    # "axadp-badalt": {
    #     "host": "10.10.100.24",
    #     "username": "admin",
    #     "password": "a10",
    #     "protocol": "https",
    #     "v_method": "ADP",
    #     "shared_partition": "mypart",
    # },
    "axadp-alt": {
        "host": "10.10.100.24",
        "username": "admin",
        "password": "a10",
        "protocol": "https",
        "v_method": "LSI",
        "shared_partition": "mypart",
    },
    "axadp-noalt": {
        "host": "10.10.100.24",
        "username": "admin",
        "password": "a10",
        "protocol": "https",
        "v_method": "LSI"
    },
    "ax-nowrite": {
        "host": "10.10.100.24",
        "username": "admin",
        "password": "a10",
        "protocol": "https",
        "write_memory": False,
    },
    "ax-write": {
        "host": "10.10.100.24",
        "username": "admin",
        "password": "a10",
        "protocol": "https",
    },
    "axipinip": {
        "host": "10.48.5.219",
        "protocol": "https",
        "username": "admin",
        "password": "a10",
        "status": True,
        "api_version": "2.1",
        "max_instance": 5000,
        "use_float": True,
        "ipinip": True
    },
}

vthunder = {
    'username': 'admin',
    'password': 'a10',

    'api_version': '3.0',

    'nova_flavor': 'acos.min',
    'glance_image': '80bf6b06-8481-485b-a3ae-87a21bde2438',

    'vthunder_tenant_name': 'admin',
    'vthunder_tenant_username': 'admin',
    'vthunder_tenant_password': 'password',

    'vthunder_management_network': 'private',
    'vthunder_data_networks': ['vipnet', 'membernet'],

    'sflow_collector': {"host": "10.10.10.10", "port": 6343},

    'license_manager': {
        "hosts": [
                {"ip": "licenseserver.com", "port": 443}
        ],
        "serial": "SNTHISISNOTREAL",
        "instance-name": "UNITTESTINSTANCE",
        "bandwidth-base": 100,
        "interval": 3,
        "use-mgmt-port": True
    },
    'write_memory': False

}

image_defaults = {
    "name": None,
    "id": None,
    "visibility": "private",
    "tags": ["a10"],
    "properties": None,
    "container_format": "bare",
    "disk_format": "qcow2",
    "min_disk": 10,
    "min_ram": 4096,
    "protected": False
}

instance_defaults = {
    "flavor": "acos.min",
    "networks": ["private", "private", "private"]
}

neutron_config = "/etc/neutron/neutron.conf"
scaling_monitor = {"ip": "127.0.0.1", "port": 2358}

# For provider based config testing

who_should_win = 'daleks'
best_spaceship = 'tardis'

providers = {
    'prov1': {
        'who_should_win': 'the-doctor',
        'vthunder': {
            'api_version': '9.9'
        }
    }
}
