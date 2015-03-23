# Copyright 2014, Doug Wiegley (dougwig), A10 Networks
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

import logging

import acos_client.errors as acos_errors

import a10_neutron_lbaas.a10_exceptions as a10_ex

LOG = logging.getLogger(__name__)


class PersistHandler(object):

    def __init__(self, c, context, pool, deprecated_arg=None):
        self.c = c
        self.context = context
        self.pool = pool
        self.c_pers = None
        self.s_pers = None

        if pool:
            self.name = pool.id

        if pool and pool.sessionpersistence:
            self.sp = pool.sessionpersistence
            if self.sp.type == 'HTTP_COOKIE':
                self.c_pers = self.name
            elif self.sp.type == 'SOURCE_IP':
                self.s_pers = self.name
            else:
                raise a10_ex.UnsupportedFeature()
        else:
            self.sp = None

    def c_persistence(self):
        return self.c_pers

    def s_persistence(self):
        return self.s_pers

    def create(self):
        if self.sp is None:
            return

        methods = {
            'HTTP_COOKIE':
                self.c.client.slb.template.cookie_persistence.create,
            'SOURCE_IP':
                self.c.client.slb.template.src_ip_persistence.create,
        }
        if self.sp.type in methods:
            try:
                methods[self.sp.type](self.name)
            except acos_errors.Exists:
                pass

    def delete(self):
        if self.sp is None:
            return

        methods = {
            'HTTP_COOKIE':
                self.c.client.slb.template.cookie_persistence.delete,
            'SOURCE_IP':
                self.c.client.slb.template.src_ip_persistence.delete,
        }
        if self.sp.type in methods:
            try:
                methods[self.sp.type](self.name)
            except Exception:
                pass
