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

import neutron_lbaas.services.loadbalancer.constants as lb_const


def to_array(in_tuple):
    for pair in in_tuple:
        yield [x for x in pair]


def to_gen(in_array, gen_type=tuple):
    for i in in_array:
        yield gen_type(i)


def to_tuple(gen):
    return tuple(x for x in to_gen(gen))


prot_array = [x for x in to_array(lb_const.LISTENER_POOL_COMPATIBLE_PROTOCOLS)]

prot_array.append(("HTTPS", "HTTP"))
lb_const.LISTENER_POOL_COMPATIBLE_PROTOCOLS = to_tuple(prot_array)
