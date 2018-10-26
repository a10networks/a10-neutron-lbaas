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

from contextlib import contextmanager
import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy.inspection import inspect

from a10_neutron_lbaas.db import api as db_api
import logging
LOG = logging.getLogger(__name__)


Base = db_api.get_base()


def _uuid_str():
    return str(uuid.uuid4())


def _get_date():
    return datetime.datetime.now()

def convert_to_boolean(input):
    if input:
        return True
    else:
        return False


class A10Base(Base):
    __abstract__ = True

    @classmethod
    @contextmanager
    def _query(cls, db_session=None):
        with db_api.magic_session(db_session) as db:
            yield db.query(cls)

    @classmethod
    def get(cls, key, db_session=None):
        with cls._query(db_session) as q:
            return q.get(key)

    @classmethod
    def find_all_by(cls, db_session=None, **kwargs):
        with cls._query(db_session) as q:
            return q.filter_by(**kwargs).all()

    @classmethod
    def find_by(cls, db_session=None, **kwargs):
        with cls._query(db_session) as q:
            return q.filter_by(**kwargs).first()

    @classmethod
    def find_by_attribute(cls, attribute_name, attribute, db_session=None):
        with cls._query(db_session) as q:
            return q.filter(
                getattr(cls, attribute_name) == attribute).first()

    @classmethod
    def find_all(cls, db_session=None):
        with cls._query(db_session) as q:
            return q.all()

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        # Populate all the unspecified columns with their defaults
        for key, column in inspect(cls).columns.items():
            if key not in kwargs and column.default is not None:
                arg = column.default.arg
                column_default = arg if callable(arg) else lambda: arg
                setattr(instance, key, column_default(instance))
        return instance

    @classmethod
    def create_and_save(cls, db_session=None, **kwargs):
        m = cls.create(**kwargs)
        with db_api.magic_session(db_session) as db:
            db.add(m)
            db.commit()
            return m

    def as_dict(self):
        d = dict(self.__dict__)
        d.pop('_sa_instance_state', None)
        return d

    def update(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def delete(self, db_session=None):
        db = db_session or inspect(self).session
        db.delete(self)

    created_at = sa.Column(sa.DateTime, default=_get_date, nullable=False)
    updated_at = sa.Column(sa.DateTime, default=_get_date, onupdate=_get_date, nullable=False)


class A10DeviceBase(A10Base):
    __abstract__ = True

    @classmethod
    def _get_a10_opts(cls, a10_opts):
        '''
        Takes a list of <a10_neutron_lbaas.db.models.a10_device.A10DeviceValue>
        objects and returns a dict with key value mappings of the a10_opt key
        name to a10_opt value.
        Modifies the valeu based on the data_type of the key
        '''

        a10_opts_dict = {}
        for a10_opt in a10_opts:
            if 'boolean' in a10_opt.associated_key.data_type:
                value = convert_to_boolean(int(a10_opt.value))
                a10_opts_dict[a10_opt.associated_key.name] = value
            elif 'integer' in a10_opt.associated_key.data_type:
                value = int(a10_opt.value)
                a10_opts_dict[a10_opt.associated_key.name] = value
            elif 'list' in a10_opt.associated_key.data_type:
                value = a10_opt.value.split(',')
                a10_opts_dict[a10_opt.associated_key.name] = value
            else:
                a10_opts_dict[a10_opt.associated_key.name] = a10_opt.value
        return a10_opts_dict

    @classmethod
    def find_a10_device_by(cls, db_session=None, **kwargs):
        d = {}
        with cls._query(db_session) as q:
            d = q.filter_by(**kwargs).first().as_dict()
            d.update(cls._get_a10_opts(d.pop('a10_opts')))
            LOG.debug("find_a10_device_by: %s" % (d))
        return d

    @classmethod
    def find_all_a10_devices(cls, db_session=None):
        d = {}
        with cls._query(db_session) as q:
            for x in q:
                d[x.name] = x.as_dict()
                d[x.name].update(cls._get_a10_opts(x.a10_opts))
            return d


class A10BaseMixin(object):

    id = sa.Column(sa.String(36), primary_key=True, nullable=False, default=_uuid_str)
    tenant_id = sa.Column(sa.String(36), nullable=False)
