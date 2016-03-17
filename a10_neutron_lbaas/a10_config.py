# Copyright 2014,  Doug Wiegley,  A10 Networks.
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
import os
import sys

from a10_neutron_lbaas import a10_exceptions as a10_ex
from a10_neutron_lbaas.etc import config as blank_config
from a10_neutron_lbaas.etc import defaults

LOG = logging.getLogger(__name__)


class EmptyConfig(object):
    @property
    def devices(self):
        return {}


class A10Config(object):

    def __init__(self):
        if os.path.exists('/etc/a10'):
            d = '/etc/a10'
        else:
            d = '/etc/neutron/services/loadbalancer/a10networks'
        self.config_dir = os.environ.get('A10_CONFIG_DIR', d)
        self.config_path = os.path.join(self.config_dir, "config.py")

        real_sys_path = sys.path
        sys.path = [self.config_dir]
        try:
            try:
                import config
                self.config = config
            except ImportError:
                LOG.error("A10Config couldn't find config.py in %s", self.config_dir)
                self.config = blank_config

            # Global defaults
            for dk, dv in defaults.GLOBAL_DEFAULTS.items():
                if not hasattr(self.config, dk):
                    self.config.dk = dv

            self.devices = {}
            for k, v in self.config.devices.items():
                if 'status' in v and not v['status']:
                    LOG.debug("status is False, skipping dev: %s", v)
                else:
                    for x in defaults.DEVICE_REQUIRED_FIELDS:
                        if x not in v:
                            msg = "device %s missing required value %s, skipping" % (k, x)
                            LOG.error(msg)
                            raise a10_ex.InvalidDeviceConfig(msg)

                    v['key'] = k
                    self.devices[k] = v

                    # Old configs had a name field
                    if 'name' not in v:
                        self.devices[k]['name'] = k

                    # Figure out port and protocol
                    protocol = self.devices[k].get('protocol', 'https')
                    port = self.devices[k].get(
                        'port', {'http': 80, 'https': 443}[protocol])
                    self.devices[k]['protocol'] = protocol
                    self.devices[k]['port'] = port

                    # Device defaults
                    for dk, dv in defaults.DEVICE_OPTIONAL_DEFAULTS.items():
                        if dk not in self.devices[k]:
                            self.devices[k][dk] = dv

        finally:
            sys.path = real_sys_path

        LOG.debug("A10Config, devices=%s", self.devices)

    @property
    def verify_appliances(self):
        if hasattr(self.config, 'verify_appliances'):
            return self.config.verify_appliances
        else:
            return True
