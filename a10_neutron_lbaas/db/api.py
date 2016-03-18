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
import sqlalchemy.orm

import a10_neutron_lbaas.a10_config as a10_config
import a10_neutron_lbaas.a10_exceptions as ex

a10_cfg = a10_config.A10Config()


def get_session():
    if not a10_cfg.use_database:
        raise ex.InternalError("attempted to use database when it is disabled")

    engine = sqlalchemy.create_engine(a10_cfg.database_connection)

    # # Bind the engine to the metadata of the Base class so that the
    # # declaratives can be accessed through a DBSession instance
    # Base.metadata.bind = engine

    return sqlalchemy.orm.sessionmaker(bind=engine)
