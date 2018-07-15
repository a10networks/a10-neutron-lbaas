
from neutron_lib.db import api as db
from neutron.db.models.segment import NetworkSegment, SegmentHostMapping
from neutron.db.models_v2 import IPAllocation, IPAllocationPool, Route, SubnetRoute, Port, Subnet, Network
from neutron.plugins.ml2.models import PortBinding, PortBindingLevel
from a10_neutron_lbaas.db import models

class AcosWrapper(object):
    def __init__(self, client, *args, **kwargs):
        self._client = client

    def create_vlan(self,  vlan_id, interfaces={}):
        try:
            return self._client.vlan.create(vlan_id, ve=True, **interfaces)
        except Exception as ex:
            raise ex
        
    def create_ve(self, ve_ifnum, ip, mask, use_dhcp):
        try:
            return self._client.interface.ve.create(ifnum, ip, mask, dhcp=use_dhcp)
        #TODO(mdurrant) Narrow exception handling.
        except Exception as ex:
            raise ex

    def get_ve(self, ve_ifnum):
        rv = {}
        try:
            ve = self._client.interface.ve.get_oper(ve_ifnum)
            rv = ve
        # TODO)mdurrant) Narrow exception handling
        except Exception as ex:
            raise ex
        return rv
    

class NeutronDbWrapper(object):
    """Wraps neutron DB ops for easy testing""" 
    def __init__(self, session, *args, **kwargs):
        self._session = session 

    def get_segment(self, port_id, level):
        binding_level = self._session.query(PortBindingLevel).filter_by(port_id=port_id, level=level).first()
        segment = self._session.query(NetworkSegment).filter_by(id=binding_level.segment_id).first()
        return segment

    def get_subnet(self, id):
        subnet = self._session.query(Subnet).filter_by(id)
        return subnet

