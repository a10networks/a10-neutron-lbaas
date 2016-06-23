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
from six.moves import queue
import threading
import time

LOG = logging.getLogger(__name__)


class WorkerThread(threading.Thread):

    def __init__(self, group=None, target=None, name=None, *args, **kwargs):
        LOG.info("A10 worker thread, initializing")
        super(WorkerThread, self).__init__(
            group=group, target=target, name=name, args=args, kwargs=kwargs)
        self.a10_driver = kwargs.get('a10_driver')
        self.sleep_timer = kwargs.get('sleep_timer')
        self.status_update = kwargs.get('status_update')
        LOG.info("====A10_DRIVER:  {0}".format(self.a10_driver.openstack_driver))
        self.plugin = self.a10_driver.openstack_driver.plugin
        self.worker_queue = queue.Queue()

    def run(self):
        LOG.info("A10 worker thread, starting")

        while True:
            try:
                oper = self.worker_queue.get()
                self.preform_operation(oper)
                self.worker_queue.task_done()
                LOG.info("===RAN OPERATIONS==")
            except queue.Empty:
                LOG.info("Queue is empty")
                time.sleep(self.sleep_timer)

            finally:
                LOG.info("A10 worker, idling")
                #self.status_update(self.a10_driver)

    def preform_operation(self, oper):
        try:
            func = oper[0]
            args = oper[1:]
            func(*args)
        
        except Exception as e:
            LOG.info(e)

    def add_to_queue(self, oper):
        self.worker_queue.put(oper)
        LOG.info("=====OPER====: {0}".format(oper))
