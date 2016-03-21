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
import runpy
import sys

import a10_neutron_lbaas.install.blank_config as blank_config

LOG = logging.getLogger(__name__)


class Config(object):
    pass


def load(path):
    config_dict = runpy.run_path(path)
    config = Config()
    config.__dict__.update(config_dict)
    return config


class A10Config(object):

    DEVICE_DEFAULTS = {
        "status": True,
        "autosnat": True,
        "api_version": "2.1",
        "v_method": "LSI",
        "max_instance": 5000,
        "use_float": False,
        "method": "hash",
        "protocol": "https"
    }

    IMAGE_DEFAULTS = {
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

    INSTANCE_DEFAULTS = {
        "flavor": "acos.min",
        "networks": ["private", "private", "private"]
    }

    def device_defaults(self, device_config):
        device = self.DEVICE_DEFAULTS.copy()
        device.update(device_config)

        # Figure out port
        protocol = device['protocol']
        port = device.get(
            'port', {'http': 80, 'https': 443}[protocol])
        device['port'] = port

        return device

    def __init__(self, config_dir=None, config=None):
        self.config = config
        if self.config is None:
            if os.path.exists('/etc/a10'):
                d = '/etc/a10'
            else:
                d = '/etc/neutron/services/loadbalancer/a10networks'
            self.config_dir = config_dir or os.environ.get('A10_CONFIG_DIR', d)
            self.config_path = os.path.join(self.config_dir, "config.py")

            try:
                self.config = load(self.config_path)
            except ImportError:
                LOG.error("A10Config couldn't find config.py in %s", self.config_dir)
                self.config = blank_config

        self.devices = {}
        for k, v in self.config.devices.items():
            if 'status' in v and not v['status']:
                LOG.debug("status is False, skipping dev: %s", v)
            else:
                device = self.device_defaults(v)
                device['key'] = k
                self.devices[k] = device

        self.image_defaults = self.IMAGE_DEFAULTS.copy()
        self.image_defaults.update(getattr(self.config, "image_defaults", {}))

        self.instance_defaults = self.INSTANCE_DEFAULTS.copy()
        self.instance_defaults.update(getattr(self.config, "instance_defaults", {}))

        LOG.debug("A10Config, devices=%s", self.devices)

    @property
    def verify_appliances(self):
        if hasattr(self.config, 'verify_appliances'):
            return self.config.verify_appliances
        else:
            return True
