#   Copyright 2014-2016,  A10 Networks
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

import sqlalchemy as sa
import sqlalchemy.orm as orm

from a10_neutron_lbaas.db import model_base


class Certificate(model_base.A10BaseMixin, model_base.A10Base):
    __tablename__ = "a10_certificates"
    name = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text(1024), nullable=True)
    cert_data = sa.Column(sa.Text(8000), nullable=False)
    key_data = sa.Column(sa.Text(8000), nullable=False)
    intermediate_data = sa.Column(sa.Text(8000), nullable=True)
    password = sa.Column(sa.String(1024), nullable=True)


class CertificateListenerBinding(model_base.A10BaseMixin, model_base.A10Base):
    __tablename__ = "a10_certificatelistenerbindings"
    certificate_id = sa.Column(sa.String(36), sa.ForeignKey("a10_certificates.id"),
                               nullable=False)
    certificate = orm.relationship(Certificate, uselist=False)
    listener_id = sa.Column(sa.String(36), nullable=False)
    # This is a TINYINT/BYTE field depending on SQL implementation
    status = sa.Column(sa.Integer(), default=0, nullable=False, server_default="0")
