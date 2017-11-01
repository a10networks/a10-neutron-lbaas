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
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker

from a10_neutron_lbaas.tests.db import session
from a10_neutron_lbaas.tests import test_case


class DbTestBase(test_case.TestCase):

    def setUp(self):
        self._undo = []
        url = os.getenv("PIFPAF_URL")
        if not url:
            self.skipTest("No database URL set")

        sa_url = make_url(url)

        if sa_url.drivername == 'mysql':
            sa_url.drivername = 'mysql+pymysql'

        initial_engine = sqlalchemy.create_engine(str(sa_url))
        initial_connection = initial_engine.connect()
        self._undo.append(initial_connection.close)
        initial_connection.execute("CREATE DATABASE a10_test_db")
        self._undo.append(lambda: initial_engine.execute("DROP DATABASE a10_test_db"))

        sa_url.database = 'a10_test_db'
        self.engine = sqlalchemy.create_engine(str(sa_url))
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
