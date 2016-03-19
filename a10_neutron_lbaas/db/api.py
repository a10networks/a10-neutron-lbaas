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


import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm

import a10_neutron_lbaas.a10_config as a10_config
import a10_neutron_lbaas.a10_exceptions as ex

Base = sqlalchemy.ext.declarative.declarative_base()
a10_cfg = a10_config.A10Config()


def get_base():
    return Base


def get_engine(url=None):
    if url is None:
        if not a10_cfg.use_database:
            raise ex.InternalError("attempted to use database when it is disabled")
        url = a10_cfg.database_connection

    return sqlalchemy.create_engine(url)


def get_session(url=None):
    DBSession = sqlalchemy.orm.sessionmaker(bind=get_engine())
    return DBSession()
