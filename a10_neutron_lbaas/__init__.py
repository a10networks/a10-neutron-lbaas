# Copyright 2014, Doug Wiegley (dougwig), A10 Networks
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
# flake8: noqa

# Version foo

from version import VERSION
from version import VERSION as __version__

# Make sure the '_' function works, as others need it

import gettext
import six

if six.PY2:
    gettext.install('a10', unicode=1)
else:
    gettext.install('a10')

# Automatically export some driver entry points

try:
    import neutron  # noqa
except ImportError:
    # Maybe running tests or utilties?
    pass
else:
    from a10_openstack_lb import A10OpenstackLBV1

try:
    import neutron  # noqa
    import neutron_lbaas  # noqa
except ImportError:
    # Maybe running tests or utilties?
    pass
else:
    from a10_openstack_lb import A10OpenstackLBV2
