# Copyright 2015, A10 Networks
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
import neutron_lbaas.common.cert_manager.barbican_cert_manager as bcm


class CertManagerWrapper(object):
    def __init__(self, certmgr=None):
        if certmgr is not None:
            self.certmgr = certmgr
        else:
            self.certmgr = bcm.CertManager()

    def get_certificate(self, cert_id, **kwargs):
        return self.certmgr.get_cert(cert_id, **kwargs)
