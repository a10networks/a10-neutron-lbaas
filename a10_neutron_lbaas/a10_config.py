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

LOG = logging.getLogger(__name__)


class A10Config(object):

    DEVICE_DEFAULTS = {
        "status": True,
        "autosnat": True,
        "api_version": "2.1",
        "v_method": "LSI",
        "max_instance": 5000,
        "use_float": False,
        "method": "hash"
    }

    def __init__(self):
        self.config_dir = os.environ.get(
            'A10_CONFIG_DIR',
            '/etc/neutron/services/loadbalancer/a10networks')
        self.config_path = os.path.join(self.config_dir, "config.py")

        real_sys_path = sys.path
        sys.path = [self.config_dir]
        try:
            import config
            self.config = config
            self.devices = {}
            for k, v in self.config.devices.items():
                if 'status' in v and not v['status']:
                    LOG.debug("status is False, skipping dev: %s", v)
                else:
                    self.devices[k] = v

                    # Figure out port and protocol
                    protocol = self.devices[k].get('protocol', 'https')
                    port = self.devices[k].get(
                        'port', {'http': 80, 'https': 443}[protocol])
                    self.devices[k]['protocol'] = protocol
                    self.devices[k]['port'] = port

                    # Device defaults
                    for dk, dv in self.DEVICE_DEFAULTS.items():
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
