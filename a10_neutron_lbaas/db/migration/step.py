# Copyright (C) 2015, A10 Networks Inc. All rights reserved.
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

import itertools
from sqlalchemy.sql import table, column, text
import uuid


def initialize_a10_appliances_configured(conn, config):
    """Create a10_appliances_configured for devices in the config.
    Returns a mapping from device keys to a10_appliances_slb ids.
    """

    a10_appliances_configured = table(
        'a10_appliances_configured',
        column('id'),
        column('device_key'))
    select_appliances = a10_appliances_configured.select()
    appliances = conn.execute(select_appliances).fetchall()
    appliance_lookup = dict((a.device_key, a.id) for a in appliances)

    a10_appliances_slb = table(
        'a10_appliances_slb',
        column('id'),
        column('type'))
    for device_key in config.devices.keys():
        if device_key not in appliance_lookup:
            id = str(uuid.uuid4())
            insert_slb = a10_appliances_slb.insert().\
                values(id=id, type=a10_appliances_configured.name)
            print(insert_slb)
            conn.execute(insert_slb)
            insert_conf = a10_appliances_configured.insert().\
                values(id=id, device_key=device_key)
            conn.execute(insert_conf)
            appliance_lookup[device_key] = id

    return appliance_lookup


def initialize_a10_slb_v1(conn, provider, a10):
    """Create a10_slb_v1 for existing vips"""

    appliance_lookup = initialize_a10_appliances_configured(conn, a10.config)

    a10_slb_v1 = table(
        'a10_slb_v1',
        column('id'),
        column('vip_id'))
    select_vips = text(
        "SELECT vips.id, vips.tenant_id "
        "FROM vips, providerresourceassociations p "
        "WHERE vips.id = p.resource_id "
        "AND p.provider_name = :provider "
        "AND vips.id NOT IN (SELECT vip_id FROM a10_slb_v1)")
    select_vips = select_vips.bindparams(provider=provider)
    vips = itertools.imap(dict, conn.execute(select_vips).fetchall())

    a10_slb = table(
        'a10_slb',
        column('id'),
        column('type'),
        column('a10_appliance_id'))
    for vip in vips:
        id = str(uuid.uuid4())
        device = a10.hooks.select_device(vip['tenant_id'])
        appliance = appliance_lookup[device['key']]
        insert_slb = a10_slb.insert().\
            values(id=id, type=a10_slb_v1.name, a10_appliance_id=appliance)
        conn.execute(insert_slb)
        insert_vip = a10_slb_v1.insert().\
            values(id=id, vip_id=vip['id'])
        conn.execute(insert_vip)


def initialize_a10_slb_v2(conn, provider, a10):
    """Create a10_slb_v2 for existing loadbalancers"""

    appliance_lookup = initialize_a10_appliances_configured(conn, a10.config)

    a10_slb_v2 = table(
        'a10_slb_v2',
        column('id'),
        column('lbaas_loadbalancer_id'))
    select_lbs = text(
        "SELECT lb.id, lb.tenant_id "
        "FROM lbaas_loadbalancers lb, providerresourceassociations p "
        "WHERE lb.id = p.resource_id "
        "AND p.provider_name = :provider "
        "AND lb.id NOT IN (SELECT lbaas_loadbalancer_id FROM a10_slb_v2)")
    select_lbs = select_lbs.bindparams(provider=provider)
    lbs = itertools.imap(dict, conn.execute(select_lbs).fetchall())

    a10_slb = table(
        'a10_slb',
        column('id'),
        column('type'),
        column('a10_appliance_id'))
    for lb in lbs:
        id = str(uuid.uuid4())
        device = a10.hooks.select_device(lb['tenant_id'])
        appliance = appliance_lookup[device['key']]
        insert_slb = a10_slb.insert().\
            values(id=id, type=a10_slb_v2.name, a10_appliance_id=appliance)
        conn.execute(insert_slb)
        insert_lb = a10_slb_v2.insert().\
            values(id=id, lbaas_loadbalancer_id=lb['id'])
        conn.execute(insert_lb)
