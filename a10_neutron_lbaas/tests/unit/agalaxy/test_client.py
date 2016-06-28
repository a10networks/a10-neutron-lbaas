# Copyright 2016, A10 Networks
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

from a10_neutron_lbaas.tests import test_case

from a10_neutron_lbaas.agalaxy import client


class TestClient(test_case.TestCase):

    def test_init_defaults(self):
        c = client.Client('203.0.113.0.7', 'admin', 'a10')

        self.assertEqual(c.session.username, 'admin')
        self.assertEqual(c.session.password, 'a10')
        self.assertEqual(c.session.http.host, '203.0.113.0.7')
        self.assertEqual(c.session.http.port, None)
        self.assertEqual(c.session.http.protocol, 'https')
        self.assertEqual(c.session.http.verify, False)
