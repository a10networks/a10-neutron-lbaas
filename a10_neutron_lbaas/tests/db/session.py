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
#    under the License.from neutron.db import model_base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from neutron.db import model_base

# Import models to be created by create_all
import a10_neutron_lbaas.db.models
import neutron.db.models_v2
import neutron_lbaas.db.loadbalancer.loadbalancer_db
import neutron_lbaas.db.loadbalancer.models

# Suppress pep8 warnings for unused imports
assert a10_neutron_lbaas.db.models
assert neutron.db.models_v2
assert neutron_lbaas.db.loadbalancer.loadbalancer_db
assert neutron_lbaas.db.loadbalancer.models


def fake_session():
    # Don't pool connections, use a clean memory database each time
    engine = create_engine('sqlite://', poolclass=NullPool)
    # Reuse a single connection so that the created tables exist in the session
    connection = engine.connect()
    model_base.BASEV2.metadata.create_all(connection)
    Session = sessionmaker(bind=connection)

    def make_session():
        session = Session()
        # Turn off enforcing foreign key constraints
        # The db records from mocked neutron and neutron_lbaas components won't actually exist
        session.execute('PRAGMA foreign_keys=OFF')
        return session

    return (make_session, connection.close)
