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

from a10_neutron_lbaas import a10_config
from a10_neutron_lbaas.etc import config as blank_config


def empty_config():
    return a10_config.A10Config(config=blank_config)


def config(config_dict):
    config_constructor = type('config', (object,), config_dict)
    return a10_config.A10Config(config=config_constructor())
