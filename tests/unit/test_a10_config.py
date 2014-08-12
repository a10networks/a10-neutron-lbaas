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

import test_base


class TestA10Config(test_base.UnitTestBase):

    def test_verify_appliances(self):
        self.assertTrue(self.a.config.verify_appliances)

    def test_num_appliances(self):
        self.assertEqual(3, len(self.a.config.devices))

    def test_expected_ports(self):
        self.assertEqual(8443, self.a.config.devices['ax1']['port'])
        self.assertEqual(80, self.a.config.devices['ax3']['port'])
        self.assertEqual(443, self.a.config.devices['ax4']['port'])

    def test_expected_protocols(self):
        self.assertEqual('https', self.a.config.devices['ax1']['protocol'])
        self.assertEqual('http', self.a.config.devices['ax3']['protocol'])
        self.assertEqual('https', self.a.config.devices['ax4']['protocol'])

    def test_v_method(self):
        for k, v in self.a.config.devices.items():
            self.assertEqual('LSI', v['v_method'].upper())
