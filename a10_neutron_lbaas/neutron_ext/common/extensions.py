# Copyright (C) 2016, A10 Networks Inc. All rights reserved.
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

"""Provides backwards compatibility for neutron -> neutron_lib moves"""

try:
    # Get the ExtensionDescriptor class from neutron
    from neutron.api.extensions import ExtensionDescriptor as ExtensionDescriptor  # noqa
except (AttributeError, ImportError):
    # If it's not there, try neutron_lib. Else, we're hosed.
    # Only way we can deal with such breaking changes
    from neutron_lib.api.extensions import ExtensionDescriptor as ExtensionDescriptor  # noqa
