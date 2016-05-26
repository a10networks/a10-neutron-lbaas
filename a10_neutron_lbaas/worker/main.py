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
import threading
import time


import status_check

LOG = logging.getLogger(__name__)


class WorkerThread(threading.Thread):

    def __init__(self, group=None, target=None, name=None, *args, **kwargs):
        LOG.info("A10 worker thread, initializing")
        super(WorkerThread, self).__init__(
            group=group, target=target, name=name, args=args, kwargs=kwargs)
        self.a10_driver = kwargs.get('a10_driver')
        self.plugin = self.a10_driver.openstack_driver.plugin
        self.queue = kwargs.get('queue')

<<<<<<< HEAD
<<<<<<< HEAD
    def run(self):
>>>>>>> initial worker thread framework
>>>>>>> run is main loop, not start
        LOG.info("A10 worker thread, starting")

        while True:
            LOG.info("A10 worker, idling")
            status_check.status_update(self.a10_driver)
            time.sleep(10)
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> initial worker thread framework
>>>>>>> run is main loop, not start
    def join(self, timeout=None):
        self.halt.set()
<<<<<<< HEAD
        super(WorkerThread, self).join(timeout)
>>>>>>> Pep8 fixes and added required dependency
