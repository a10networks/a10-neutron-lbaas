# Copyright 2015,  A10 Networks
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

from sqlalchemy.ext.declarative import clsregistry

from a10_neutron_lbaas.db import api as db_api

# Import models to be created by create_all
import a10_neutron_lbaas.db.models
import a10_neutron_lbaas.db.models.scaling_group

# Suppress pep8 warnings for unused imports
assert a10_neutron_lbaas.db.models
assert a10_neutron_lbaas.db.models.scaling_group

Base = db_api.get_base()


def create_tables(connection, tables=None):
    Base.metadata.create_all(connection, tables=tables)
    return connection


def a10_models():
    return [model for model in Base._decl_class_registry.values()
            if not isinstance(model, clsregistry._ModuleMarker)]


def insert_a10_keys(db_session):
    keys = [
        {'name': 'ipinip', 'default_value': '0', 'data_type': 'boolean'},
        {'name': 'autosnat', 'default_value': '0', 'data_type': 'boolean'},
        {'name': 'use_float', 'default_value': '0', 'data_type': 'boolean'},
        {'name': 'v_method', 'default_value': 'LSI', 'data_type': 'string'},
        {'name': 'write_memory', 'default_value': '1', 'data_type': 'boolean'},
        {'name': 'source_nat_pool', 'default_value': '', 'data_type': 'string'},
        {'name': 'conn_limit', 'default_value': '8000000', 'data_type': 'string'},
        {'name': 'shared_partition', 'default_value': 'shared', 'data_type': 'string'},
        {'name': 'default_virtual_server_vrid', 'default_value': '', 'data_type': 'string'}]
    for key in keys:
        a10_neutron_lbaas.db.models.A10DeviceKey.create_and_save(db_session=db_session, **key)
