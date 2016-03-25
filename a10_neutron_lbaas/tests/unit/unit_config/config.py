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
    "axadp-alt": {
        "host": "10.10.100.24",
        "username": "admin",
        "password": "a10",
        "protocol": "https",
        "v_method": "ADP",
        "shared_partition": "mypart",
    },
    "axadp-noalt": {
        "host": "10.10.100.24",
        "username": "admin",
        "password": "a10",
        "protocol": "https",
        "v_method": "ADP"
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
