
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


def hm_type(c, os_hm_type):
    hm_map = {
        'PING': c.client.slb.hm.ICMP,
        'TCP': c.client.slb.hm.TCP,
        'HTTP': c.client.slb.hm.HTTP,
        'HTTPS': c.client.slb.hm.HTTPS
    }
    return hm_map[os_hm_type]


def service_group_lb_method(c, os_method):
    z = c.client.slb.service_group
    lb_methods = {
        'ROUND_ROBIN': z.ROUND_ROBIN,
        'LEAST_CONNECTIONS': z.LEAST_CONNECTION,
        'SOURCE_IP': z.WEIGHTED_LEAST_CONNECTION,
        'WEIGHTED_ROUND_ROBIN': z.WEIGHTED_ROUND_ROBIN,
        'WEIGHTED_LEAST_CONNECTION': z.WEIGHTED_LEAST_CONNECTION,
        'LEAST_CONNECTION_ON_SERVICE_PORT':
            z.LEAST_CONNECTION_ON_SERVICE_PORT,
        'WEIGHTED_LEAST_CONNECTION_ON_SERVICE_PORT':
            z.WEIGHTED_LEAST_CONNECTION_ON_SERVICE_PORT,
        'FAST_RESPONSE_TIME': z.FAST_RESPONSE_TIME,
        'LEAST_REQUEST': z.LEAST_REQUEST,
        'STRICT_ROUND_ROBIN': z.STRICT_ROUND_ROBIN,
        'STATELESS_SOURCE_IP_HASH': z.STATELESS_SOURCE_IP_HASH,
        'STATELESS_DESTINATION_IP_HASH': z.STATELESS_DESTINATION_IP_HASH,
        'STATELESS_SOURCE_DESTINATION_IP_HASH':
            z.STATELESS_SOURCE_DESTINATION_IP_HASH,
        'STATELESS_PER_PACKET_ROUND_ROBIN':
            z.STATELESS_PER_PACKET_ROUND_ROBIN,
    }
    return lb_methods[os_method]


# This is duplicated because v1/v2 have different mappings.
# TODO(mdurrant) Refactor this into a dictionary that encapsulates v1/v2 differences.
def service_group_lb_method_v2(c, os_method):
    z = c.client.slb.service_group
    lb_methods = {
        'ROUND_ROBIN': z.ROUND_ROBIN,
        'LEAST_CONNECTIONS': z.LEAST_CONNECTION,
        'SOURCE_IP': 'src-ip-hash',
        'WEIGHTED_ROUND_ROBIN': z.WEIGHTED_ROUND_ROBIN,
        'WEIGHTED_LEAST_CONNECTION': z.WEIGHTED_LEAST_CONNECTION,
        'LEAST_CONNECTION_ON_SERVICE_PORT':
            z.LEAST_CONNECTION_ON_SERVICE_PORT,
        'WEIGHTED_LEAST_CONNECTION_ON_SERVICE_PORT':
            z.WEIGHTED_LEAST_CONNECTION_ON_SERVICE_PORT,
        'FAST_RESPONSE_TIME': z.FAST_RESPONSE_TIME,
        'LEAST_REQUEST': z.LEAST_REQUEST,
        'STRICT_ROUND_ROBIN': z.STRICT_ROUND_ROBIN,
        'STATELESS_SOURCE_IP_HASH': z.STATELESS_SOURCE_IP_HASH,
        'STATELESS_DESTINATION_IP_HASH': z.STATELESS_DESTINATION_IP_HASH,
        'STATELESS_SOURCE_DESTINATION_IP_HASH':
            z.STATELESS_SOURCE_DESTINATION_IP_HASH,
        'STATELESS_PER_PACKET_ROUND_ROBIN':
            z.STATELESS_PER_PACKET_ROUND_ROBIN,
    }
    return lb_methods[os_method]


def service_group_protocol(c, os_protocol):
    z = c.client.slb.service_group
    protocols = {
        'HTTP': z.TCP,
        'HTTPS': z.TCP,
        'TERMINATED_HTTPS': z.TCP,
        'TCP': z.TCP,
        'UDP': z.UDP
    }
    return protocols[os_protocol]


def vip_protocols(c, os_protocol):
    z = c.client.slb.virtual_server.vport
    protocols = {
        'TCP': z.TCP,
        'UDP': z.UDP,
        'HTTP': z.HTTP,
        'HTTPS': z.TCP,
        'TERMINATED_HTTPS': z.HTTPS,
        'OTHERS': z.OTHERS,
        'RTSP': z.RTSP,
        'FTP': z.FTP,
        'MMS': z.MMS,
        'SIP': z.SIP,
        'FAST_HTTP': z.FAST_HTTP,
        'GENERIC_PROXY': z.GENERIC_PROXY,
        'SSL_PROXY': z.SSL_PROXY,
        'SMTP': z.SMTP,
        'SIP_TCP': z.SIP_TCP,
        'SIPS': z.SIPS,
        'DIAMETER': z.DIAMETER,
        'DNS_UDP': z.DNS_UDP,
        'TFTP': z.TFTP,
        'DNS_TCP': z.DNS_TCP,
        'RADIUS': z.RADIUS,
        'MYSQL': z.MYSQL,
        'MSSQL': z.MSSQL,
        'FIX': z.FIX,
        'SMPP_TCP': z.SMPP_TCP,
        'SPDY': z.SPDY,
        'SPDYS': z.SPDYS,
        'FTP_PROXY': z.FTP_PROXY
    }
    return protocols[os_protocol]
