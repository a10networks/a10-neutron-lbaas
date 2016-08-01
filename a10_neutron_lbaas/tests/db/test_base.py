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

import os

import sqlalchemy
from sqlalchemy.orm import sessionmaker
import sqlalchemy_utils as sa_utils

from a10_neutron_lbaas.tests.db import session
from a10_neutron_lbaas.tests import test_case


class DbTestBase(test_case.TestCase):

    def setUp(self):
        self._undo = []
        url = os.getenv("PIFPAF_URL")
        if not url:
            self.skipTest("No database URL set")

        if url.startswith('mysql:'):
            url = url.replace('mysql', 'mysql+pymysql', 1)
        if not sa_utils.database_exists(url):
            sa_utils.create_database(url)
            self._undo.append(lambda: sa_utils.drop_database(url))

        self.engine = sqlalchemy.create_engine(url)
        self.connection = self.engine.connect()
        self._undo.append(self.connection.close)

    def tearDownDb(self):
        while (self._undo):
            self._undo.pop()()

    def tearDown(self):
        self.tearDownDb()


class UnitTestBase(DbTestBase):

    def setUp(self):
        super(UnitTestBase, self).setUp()

        try:
            session.create_tables(self.connection)
        except Exception as e:
            # tearDown doesn't run if setUp throws an exception!
            self.tearDownDb()
            raise e

        Session = sessionmaker(bind=self.connection)
        self.open_session = Session
