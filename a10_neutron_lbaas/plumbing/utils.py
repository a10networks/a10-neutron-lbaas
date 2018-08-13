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
            candidate = str(ipaddr((in_range-in_use).pop()))
        except:
            LOG.error("Could not allocate IP address for range:{0}-{1}".format(
                ip_range_begin, ip_range_end))
        finally:
            return candidate
