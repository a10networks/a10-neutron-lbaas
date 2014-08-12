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


class HandlerBase(object):

    def __init__(self, a10_driver):
        self.a10_driver = a10_driver
        self.openstack_driver = self.a10_driver.openstack_driver


# for a10 v1 driver:

# # def _active(self, context, model, vid):
# #     self.plugin.update_status(context, model, vid, constants.ACTIVE)

# # def _failed(self, context, model, vid):
# #     self.plugin.update_status(context, model, vid, constants.ERROR)


# def _db_delete

# def _pool_total()

        #this:
        #     self.plugin.update_pool_health_monitor(context,
        #                                            health_monitor["id"],
        #                                            pool_id,
        #                                            constants.ACTIVE)
        # except Exception:
        #     self.plugin.update_pool_health_monitor(context,
        #                                            health_monitor["id"],
        #                                            pool_id,
        #                                            constants.ERROR)

        #     hm_binding_qty = (context.session.query(
        #         lb_db.PoolMonitorAssociation
        #     ).filter_by(monitor_id=health_monitor['id']).join(lb_db.Pool)
        #         .count())

        #     self.plugin._delete_db_pool_health_monitor(context,
        #                                                health_monitor['id'],
        #                                                pool_id)

    # def _get_vip_id(self, pool_id):
    #     return self.openstack_driver._pool_get_vip_id(pool_id)
    #     # pool_qry = context._session.query(lb_db.Pool).filter_by(id=pool_id)
        # vip_id = pool_qry.vip_id

    # def _get_hm(self, hm_id):
    #     return self.openstack_driver._pool_get_hm(hm_id)
    #             # hmon = self.plugin.get_health_monitor(context, hm['monitor_id'])
