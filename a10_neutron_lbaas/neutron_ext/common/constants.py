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

A10_APPLIANCE_EXT = 'a10-appliance'
A10_APPLIANCE = "A10_APPLIANCE"

A10_IMAGE_EXT = 'a10-image'
A10_IMAGE = "A10_IMAGE"

nconstants.EXT_TO_SERVICE_MAPPING[A10_APPLIANCE_EXT] = A10_APPLIANCE
nconstants.EXT_TO_SERVICE_MAPPING[A10_IMAGE_EXT] = A10_IMAGE
try:
    nconstants.ALLOWED_SERVICES.append(A10_APPLIANCE)
    nconstants.ALLOWED_SERVICES.append(A10_IMAGE)
    nconstants.COMMON_PREFIXES[A10_APPLIANCE] = ""
    nconstants.COMMON_PREFIXES[A10_IMAGE] = ""
except AttributeError:
    # In Liberty and later, ALLOWED_SERVICES is derived from EXT_TO_SERVICE_MAPPING
    # COMMON_PREFIXES are instead gotten from plugin.path_prefix
    pass
