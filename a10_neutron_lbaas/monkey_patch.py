# Copyright 2014, A10 Networks
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


class MonkeyPatch(object):

    def __init__(self, plugin):
        self.plugin = plugin

    def stats(self, context, loadbalancer_id):
        lb = self.plugin.db.get_loadbalancer(context, loadbalancer_id)
        driver = self.plugin._get_driver_for_loadbalancer(context, loadbalancer_id)
        stats_data = driver.load_balancer.stats(context, lb)
        if stats_data:
            self.plugin.db.update_loadbalancer_stats(context, loadbalancer_id,
                                                     stats_data)
        db_stats = self.plugin.db.stats(context, loadbalancer_id)
        setattr(db_stats, "extended_stats", stats_data['extended_stats'])
        return {'stats': db_stats.to_api_dict()}
