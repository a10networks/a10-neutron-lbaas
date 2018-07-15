from neutron.db.models.segment import NetworkSegment, SegmentHostMapping
from neutron.db.models_v2 import IPAllocation, IPAllocationPool, Route, SubnetRoute, Port, Subnet, Network
from neutron_lib.db import api as db_api

def get_port_dependencies(network_id, network_type=None):
    """Returns the networks, subnet, segment"""

    session = db_api.get_reader_session()

    query_args = {
        "network_id": network_id
    }

    if network_type:
        query_args["network_type"] = network_type


def get_network_segment(network_id, network_type=None):

    session = db_api.get_reader_session()
    query_args = {
        "network_id": network_id
    }

    if network_type:
        query_args["network_type"] = network_type

    segment = session.query(NetworkSegment).filter_by(**query_args).first()
    return segment
