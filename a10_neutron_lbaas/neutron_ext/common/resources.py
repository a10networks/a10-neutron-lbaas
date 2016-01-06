# Copyright 2016,  A10 Networks
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

import collections

from neutron.api.v2 import attributes

import six


def remove_attributes_not_specified(resource):
    return dict((k, v) for k, v in resource.items() if v != attributes.ATTR_NOT_SPECIFIED)


def apply_template(template, *args, **kw):
    """Applies every callable in any Mapping or Iterable"""

    if six.callable(template):
        return template(*args, **kw)
    if isinstance(template, six.string_types):
        return template
    if isinstance(template, collections.Mapping):
        return template.__class__((k, apply_template(v, *args, **kw)) for k, v in template.items())
    if isinstance(template, collections.Iterable):
        return template.__class__(apply_template(v, *args, **kw) for v in template)
    return template
