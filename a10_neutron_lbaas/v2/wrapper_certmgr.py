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

    # neutron-lbaas barbican interface changed in Mitaka
    # https://github.com/openstack/neutron-lbaas/commit/2228ef86ab7caf986a8608800d41add6cbd7f5f7

    def get_certificate(self, container_id, project_id=None,
                        resource_ref=None, **kwargs):
        try:
            return self.certmgr.get_cert(container_id, **kwargs)
        except TypeError:
            return self.certmgr.get_cert(project_id, container_id, resource_ref, **kwargs)

    def store_cert(self, certificate, private_key, intermediates=None,
                   private_key_passphrase=None, expiration=None,
                   name='A10-LBaaS TLS Cert',
                   project_id=None, **kwargs):
        try:
            return self.certmgr.store_cert(certificate, private_key,
                                           intermediates=intermediates,
                                           private_key_passphrase=private_key_passphrase,
                                           expiration=expiration, name=name, **kwargs)
        except TypeError:
            return self.certmgr.store_cert(project_id, certificate, private_key,
                                           intermediates=intermediates,
                                           private_key_passphrase=private_key_passphrase,
                                           expiration=expiration, name=name, **kwargs)

    def delete_cert(self, cert_ref, service_name='A10-LBaaS', resource_ref=None,
                    project_id=None, **kwargs):
        try:
            return self.certmgr.delete_cert(cert_ref, service_name=service_name,
                                            resource_ref=resource_ref, **kwargs)
        except TypeError:
            return self.certmgr.delete_cert(project_id, cert_ref, resource_ref,
                                            service_name=service_name, **kwargs)
