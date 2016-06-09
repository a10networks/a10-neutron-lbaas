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

from neutron.plugins.common import constants as nconstants

from a10_openstack_lib.resources import a10_device_instance

A10_DEVICE_INSTANCE_EXT = a10_device_instance.EXTENSION
A10_DEVICE_INSTANCE = a10_device_instance.SERVICE

nconstants.EXT_TO_SERVICE_MAPPING[A10_DEVICE_INSTANCE_EXT] = A10_DEVICE_INSTANCE
try:
    nconstants.ALLOWED_SERVICES.append(A10_DEVICE_INSTANCE)
    nconstants.COMMON_PREFIXES[A10_DEVICE_INSTANCE] = ""
except AttributeError:
    # In Liberty and later, ALLOWED_SERVICES is derived from EXT_TO_SERVICE_MAPPING
    # COMMON_PREFIXES are instead gotten from plugin.path_prefix
    pass
