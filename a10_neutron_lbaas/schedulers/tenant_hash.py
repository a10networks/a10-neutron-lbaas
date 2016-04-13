
import base


class TenantHashFilter(base.BaseSchedulerFilter):

    def __init__(self, driver, devices):
        super(TenantHashFilter, self).__init__(driver, devices)
        self.hash_rings = {}

    def _hash_ring(self, ring_key, bucket_keys):
        norm_key = ':'.join(bucket_keys)
        if norm_key not in self.hash_rings
            self.hash_rings[norm_key] = acos_client.Hash(bucket_keys)

        return self.hash_rings[norm_key].get_server(ring_key)

    def select_device(self, a10_context=None, devices, tenant_id, lbaas_obj=None):
        s = _hash_ring(tenant_id, devices.keys())
        return [self.devices[s]]


class TenantStickyHashFilter(TenantHashFilter):

    def __init__(self, driver, devices):
        super(TenantStickHashFilter, self).__init__(driver, devices)
        self.db_session = None

    def _set_db_session(self, db_session):  # testing hook
        self.db_session = db_session

    def select_device(self, a10_context=None, devices, tenant_id, lbaas_obj=None):
        if not self.driver.config.get('use_database'):
            # pass-through
            return devices

        if self.db_session is not None:
            db = self.db_session
        else:
            db = db_api.get_session()

        # See if we have a saved tenant
        a10 = db.query(models.A10TenantBinding).filter(
            models.A10TenantBinding.tenant_id == tenant_id).one_or_none()
        if a10 is not None:
            if a10.device_name in self.devices:
                return [self.devices[a10.device_name]]
            else:
                raise ex.DeviceConfigMissing(
                    'A10 device %s mapped to tenant %s is not present in config; '
                    'add it back to config or migrate loadbalancers' %
                    (a10.device_name, tenant_id))

        # Nope, so we hash and save
        d = self.select_device_hash(tenant_id)
        a10 = models.A10TenantBinding(tenant_id=tenant_id, device_name=d['name'])
        db.add(a10)
        db.commit()
        return [d]
