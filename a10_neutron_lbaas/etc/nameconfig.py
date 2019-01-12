# Copyright 2014-2019, A10 Networks
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

vport_expressions = {
    "secure scaleout": {
        "regex": "^secure",
        "json": {
            "scaleout-bucket-count": 128
        }
    }
}

virtual_server_expressions = {
    "described": {
        "regex": "^desc",
        "json": {
            "description": "Described from the name"
        }
    }
}

service_group_expressions = {
    "mon1": {
        "regex": "^mon",
        "json": {
            "health-check": "mon1"
        }
    }
}

member_expressions = {
    "connections42": {
        "regex": "^connlimit",
        "json": {
            "conn-limit": 4200
        }
    }
}

monitor_expressions = {
    "monitor": {
        "regex": "^tagged",
        "json": {
            "user-tag": 42
        }
    }
}
