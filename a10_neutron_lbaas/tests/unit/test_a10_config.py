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
        # Everytime we update the test config, this test has to be updated
        # A better test would seem to be be parsing the JSON structure found in the file
        # and comparing that against what we get in devices.
        # This actually tests the number of devices with status == True
        self.assertEqual(10, len(self.a.config.devices))

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

    def test_alternate_shared_partition(self):
        self.assertTrue(self.a.config.devices['axadp-alt']['shared_partition'])

    def test_ip_in_ip(self):
        expected = True
        actual = False
        for k, v in self.a.config.devices.items():
            if "ip_in_ip" in v:
                actual = v['ip_in_ip']
                self.assertEqual(expected, actual)
