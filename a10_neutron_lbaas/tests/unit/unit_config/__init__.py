# Copyright 2015,  A10 Networks
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
#    under the License.from neutron.db import model_base

import os

from a10_neutron_lbaas import a10_config
from a10_neutron_lbaas.install import blank_config


def setUp():
    unit_dir = os.path.dirname(__file__)
    os.environ['A10_CONFIG_DIR'] = unit_dir


def empty_config():
    config_dir = os.path.dirname(blank_config.__file__)
    return a10_config.A10Config(config_dir=config_dir)
