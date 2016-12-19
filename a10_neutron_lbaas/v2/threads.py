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

import threading
from threading import Thread


class StatThread(object):

    def __init__(self):
        self.stats = {}
        self.lock = threading.Lock()

    def start(self, **kwargs):
        t = Thread(target=self._stats_thread, kwargs=kwargs)
        t.start()

    def _stats_thread(self, **kwargs):
        for k, v in kwargs.items():
            with self.lock:
                if self.stats.get(k):
                    self.stats[k] += v
                else:
                    self.stats[k] = v

