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

from a10_neutron_lbaas.acos import openstack_mappings as target
from a10_neutron_lbaas.tests.unit import test_base

import mock


class TestA10Openstack(test_base.UnitTestBase):

    def test_source_ip_v2(self):
        mock_client = mock.Mock()
        mock_client.client.slb.service_group.SOURCE_IP_HASH = 'SOURCE_IP'
        expected = mock_client.client.slb.service_group.SOURCE_IP_HASH
        actual = target.service_group_lb_method(mock_client, 'SOURCE_IP')
        self.assertEqual(expected, actual)
