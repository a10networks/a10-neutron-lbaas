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

from sqlalchemy.orm import sessionmaker

from a10_neutron_lbaas.db import api as db_api

Base = db_api.get_base()


def fake_connection(tables=None):
    # Don't pool connections, use a clean memory database each time
    engine = db_api.get_engine('sqlite://')
    # Reuse a single connection so that the created tables exist in the session
    connection = engine.connect()
    Base.metadata.create_all(connection, tables=tables)
    return connection


def fake_session(tables=None):
    connection = fake_connection(tables)
    Session = sessionmaker(bind=connection)

    def make_session():
        session = Session()
        # Turn off enforcing foreign key constraints
        session.execute('PRAGMA foreign_keys=OFF')
        return session

    return (make_session, connection.close)


def a10_neutron_lbaas_models():
    return [model
            for model in Base._decl_class_registry.values()
            if model.__module__.startswith('a10_neutron_lbaas.')]


def fake_migration_connection():
    a10_neutron_lbaas_tables = [model.__tablename__ for model in a10_neutron_lbaas_models()]
    other_tables = [table
                    for table in Base.metadata.sorted_tables
                    if table.name not in a10_neutron_lbaas_tables]
    return fake_connection(other_tables)
