from a10_neutron_lbaas.v2 import handler_hm
from a10_neutron_lbaas.v2 import handler_lb
from a10_neutron_lbaas.v2 import handler_listener
from a10_neutron_lbaas.v2 import handler_member
from a10_neutron_lbaas.v2 import handler_pool

class LoadBalancerQueued():

    def __init__(self, queue, a10_driver, openstack_driver, neutron):
        self.lb_h = handler_lb.LoadbalancerHandler(a10_driver, openstack_driver.load_balancer, neutron=neutron)
        self.queue = queue

    def create(self, context, lb):
        self.queue.put_nowait([self.lb_h.create, context, lb])

    def update(self, context, old_lb, lb):
        self.queue.put_nowait([self.lb_h.update, context, old_lb, lb])

    def delete(self, context, lb):
        self.queue.put_nowait([self.lb_h.delete, context, lb])

    def refresh(self, context, lb):
        self.queue.put_nowait([self.lb_h.refresh, context, lb])

    def stats(self, context, lb):
        self.queue.put_nowait([self.lb_h.stats, context, lb])

class ListenerQueued():

    def __init__(self, queue, a10_driver, openstack_driver, neutron, barbican_client):
        self.listener_h = handler_listener.ListenerHandler(a10_driver, openstack_driver.listener, neutron=neutron, barbican_client=barbican_client)
        self.queue = queue

    def create(self, context, listener):
        self.queue.put_nowait([self.listener_h.create, context, listener])
    
    def update(self, context, old_listener, listener):
        self.queue.put_nowait([self.listener_h.update, context, old_listener, listener])

    def delete(self, context, listener):
        self.queue.put_nowait([self.listener_h.delete, context, listener])

class PoolQueued():

    def __init__(self, queue, a10_driver, openstack_driver, neutron):
        self.pool_h = handler_pool.PoolHandler(a10_driver, openstack_driver.pool, neutron=neutron)
        self.queue = queue

    def create(self, context, pool):
        self.queue.put_nowait([self.pool_h.create, context, pool])

    def update(self, context, old_pool, pool):
        self.queue.put_nowait([self.pool_h.update, context, old_pool, pool])

    def delete(self, context, pool):
        self.queue.put_nowait([self.pool_h.delete, context, pool])

class MemberQueued():

    def __init__(self, queue, a10_driver, openstack_driver, neutron):
        self.pool_h = handler_member.MemberHandler(a10_driver, openstack_driver.member, neutron=neutron)
        self.queue = queue

    def create(self, context, member):
        self.queue.put_nowait([self.pool_h.create, context, member])

    def update(self, context, old_member, member):
        self.queue.put_nowait([self.pool_h.update, context, old_member, member])

    def delete(self, context, member):
        self.queue.put_nowait([self.pool_h.delete, context, member])

class HealthMonitorQueued():
   
    def __init__(self, queue, a10_driver, openstack_driver, neutron):
        self.hm_h = handler_hm.HealthMonitorHandler(a10_driver, openstack_driver.health_monitor, neutron=neutron)
        self.queue = queue

    def create(self, context, hm):
        self.queue.put_nowait([self.hm_h.create, context, hm])

    def update(self, context, old_hm, hm):
        self.queue.put_nowait([self.hm_h.update, context, old_hm, hm])

    def delete(self, context, hm):
        self.queue.put_nowait([self.hm_h.delete, context, hm])
