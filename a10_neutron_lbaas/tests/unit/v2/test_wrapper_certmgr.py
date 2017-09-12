# Copyright 2017, A10 Networks
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

import mock

from neutron_lbaas.common.cert_manager import cert_manager

from a10_neutron_lbaas.tests import test_case
from a10_neutron_lbaas.v2 import wrapper_certmgr


class TestCertManagerWrapper(test_case.TestCase):

    def setUp(self, **kwargs):
        super(TestCertManagerWrapper, self).setUp(**kwargs)

        certmgr = mock.create_autospec(cert_manager.CertManager)
        self.target = wrapper_certmgr.CertManagerWrapper(certmgr=certmgr)

    def test_get_certificate_type_checks(self):
        self.target.get_certificate('fake-container-id',
                                    project_id='fake-project-id',
                                    check_only=True)

    def test_store_cert_type_checks(self):
        self.target.store_cert('fake-certificate',
                               'fake-private-key',
                               project_id='fake-project-id')

    def test_delete_cert_type_checks(self):
        self.target.delete_cert('fake-certificate-id',
                                project_id='fake-project-id')
