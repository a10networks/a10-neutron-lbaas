# Copyright 2014-2019, A10 Networks
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

from netaddr import IPAddress as ipaddr
from netaddr import IPRange as iprange
from netaddr import IPSet as ipset

from oslo_log import log

import random

LOG = log.getLogger.__name__


class IPHelpers(object):
    @staticmethod
    def generate_random_mac(prefix):
        mac_address = [
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff)]
        mac_last = ':'.join(map(lambda x: "%02x" % x, mac_address))
        mac_address = "prefix:{0}".format(mac_last)
        return mac_address

    @staticmethod
    def find_unused_ip(ip_range_begin, ip_range_end, ips_in_use):
        candidate = None

        in_range = ipset(iprange(ip_range_begin, ip_range_end))
        in_use = ipset(ips_in_use)

        try:
            candidate = str(ipaddr((in_range - in_use).pop()))
        except Exception:
            LOG.error("Could not allocate IP address for range:{0}-{1}".format(
                ip_range_begin, ip_range_end))
        finally:
            return candidate
