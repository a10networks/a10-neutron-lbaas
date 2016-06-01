class LoadBalancerQueued():

    def __init__(self, queue, openstack_driver, neutron):
        self.lb_h = LoadbalancerHandler(self, openstack_driver.load_balancer, neutron=neutron)
        self.queue = queue

    def create(self, context, lb):
        pass

    def update(self, context, old_lb, lb):
        pass

    def delete(self, context, lb):
        pass

    def refresh(self, context, lb):
        pass

    def stats(self, context, lb):
        pass

class ListenerQueued():

    def __init__(self, queue, openstack_driver, neutron, barbican_client):
        self.listener_h = ListenerHandler(self, openstack_driver.listener, neutron=neutron, barbican_client=barbican_client)

    def create():
        pass
    
    def update():
        pass

    def delete():
        pass

class PoolQueued():

    def __init__():
        self.pool_h = PoolHandler(self, self.openstack_driver.pool, neutron=self.neutron)

    def create():
        pass

    def update():
        pass

    def delete():
        pass

class HmQueued():
   
    def __init__():
        self.hm_h = HealthMonitorHandler(self, self.openstack_driver.health_monitor, neutron=self.neutron)

    def create():
        pass

    def update():
        pass

    def delete():
        pass
