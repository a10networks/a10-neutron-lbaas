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

import logging

from acos_client import errors as acos_errors

LOG = logging.getLogger(__name__)


def initialize_licensing(vth_cfg, device_cfg, client):

    licensing = vth_cfg.get('license_manager')
    if licensing is not None:
        client.license_manager.paygo(
            llp_hosts=map(lambda host: host['ip'], licensing["hosts"]),
            sn=licensing["serial"],
            instance_name=device_cfg.get('name'),
            use_mgmt_port=licensing["use-mgmt-port"],
            bandwidth_base=licensing["bandwidth-base"],
            interval=licensing["interval"]
        )


def initialize_interfaces(vth_cfg, device_cfg, client):

    networks = vth_cfg.get("vthunder_data_networks", [])
    for x in range(1, len(networks) + 1):
        # Statically coded until we have devices that correctly configure
        # data-plane interfaces from dhcp
        client.interface.ethernet.update(x, dhcp=True, enable=True)


def initialize_dns(vth_cfg, device_cfg, client):
    dns = vth_cfg.get('dns_resolver')

    if dns is not None:
        client.dns.set(**dns)


def initialize_sflow(vth_cfg, device_cfg, client):

    collector = vth_cfg.get('sflow_collector')
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


def initialize_vthunder(a10_cfg, device_cfg, client):
    """Perform initialization of system-wide settings"""

    vth = a10_cfg.get_vthunder_config()
    initialize_interfaces(vth, device_cfg, client)
    initialize_dns(vth, device_cfg, client)
    initialize_licensing(vth, device_cfg, client)
    initialize_sflow(vth, device_cfg, client)
