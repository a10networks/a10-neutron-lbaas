# Copyright 2016, A10 Networks
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

from acos_client import errors as acos_errors


def initialize_licensing(vthunder_config, client):

    licensing = vthunder_config.get('license_manager')

    if licensing is not None:
        client.license_manager.paygo(
            llp_hosts=map(lambda host: host['ip'], licensing["hosts"]),
            sn=licensing["serial"],
            instance_name=vthunder_config.get('name') or licensing["instance-name"],
            use_mgmt_port=licensing["use-mgmt-port"],
            bandwidth_base=licensing["bandwidth-base"],
            interval=licensing["interval"]
        )


def initialize_interfaces(vthunder_config, client):

    networks = vthunder_config.get("vthunder_data_networks", [])
    for x in range(1, len(networks) + 1):
        # Statically coded until we can plumb in the right gateway
        # or, optimally, have devices that correctly configure
        # mgmt interfaces from dhcp
        client.interface.ethernet.update(x, dhcp=True, enable=True)


def initialize_sflow(vthunder_config, client):

    collector = vthunder_config.get('sflow_collector')

    if collector is None:
        return

    try:
        client.sflow.collector.ip.create(collector['host'], collector['port'])
    except acos_errors.Exists:
        pass

    try:
        client.sflow.polling.create(http_counter=1)
    except acos_errors.Exists:
        pass

    try:
        client.sflow.setting.create(None, None, None, 1)
    except acos_errors.Exists:
        pass


def initialize_vthunder(vthunder_config, client):
    """Perform initialization of system-wide settings"""

    initialize_interfaces(vthunder_config, client)
    initialize_licensing(vthunder_config, client)
    initialize_sflow(vthunder_config, client)
