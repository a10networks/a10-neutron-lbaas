

import os

from a10_neutron_lbaas import a10_config
from a10_neutron_lbaas.etc import config as blank_config


def empty_config():
    return a10_config.A10Config(config=blank_config)


def config(config_dict):
    config_constructor = type('config', (object,), config_dict)
    return a10_config.A10Config(config=config_constructor())
