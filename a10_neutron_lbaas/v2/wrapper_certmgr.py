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


class CertManagerWrapper(object):
    def __init__(self, certmgr=None, handler=None):
        if certmgr is not None:
            self.certmgr = certmgr
        else:
            self.certmgr = handler.neutron.bcm_factory()

    def get_certificate(self, container_id, **kwargs):
        return self.certmgr.get_cert(container_id, **kwargs)

    def store_cert(self, certificate, private_key, intermediates=None,
                   private_key_passphrase=None, expiration=None,
                   name='A10-LBaaS TLS Cert', **kwargs):
        return self.certmgr.store_cert(certificate, private_key, intermediates=intermediates,
                                       private_key_passphrase=private_key_passphrase,
                                       expiration=expiration, name=name, kwargs=kwargs)

    def delete_cert(self, cert_ref, service_name='A10-LBaaS', resource_ref=None,
                    **kwargs):
        return self.certmgr.delete_cert(cert_ref, service_name=service_name,
                                        resource_ref=resource_ref, kwargs=kwargs)
