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
        self.halt = self.halt = threading.Event()

    def run(self):
        LOG.info("A10 worker thread, starting")
        while not self.halt.isSet():
            try:
                LOG.info("QUEUE SIZE: " + str(self.queue.qsize()))
                LOG.info("QUEUE: " + str(self.queue))
                if not self.queue.empty():
                    oper = self.queue.get(timeout=1)


    def join(self, timeout=None):
        self.halt.set()
        super(WorkerThread, self).join(timeout)
    
    def preform_operation(self, oper):
        func = oper[0]
        args = oper[1:]
        func(*args)

    def add_to_queue(self, oper):
        self.queue.put_nowait(oper)
        LOG.info("========TRACER6======")
