

# A static list of A10 appliances used by the driver.  This list is most
# applicable to hardware appliances or long-lived vThunders.
# Note that the real list is provided in the 'providers' dictionary,
# which usually references this top one for the 'default' provider.

devices = {
    "ax1": {
        "name": "ax1",
        "host": "10.48.1.43",
        "username": "admin",
        "password": "a10",
        "api_version": "3.0",
        "v_method": "ADP",

        "status": True,
        "autosnat": True,
        "max_instance": 5000,
        "use_float": False,
        "method": "hash"

        "max_partitions":3,
        "per_partition_lif_max":10,
        "vxlan":1,
        "vlan":0,
        "gateway_mode":1,
        "zones": [
            {
                "name":"zone1",
                "vrid":1,
                "max_partitions":3,
                "vteps": [
                    {
                        "encap":"vxlan",
                        "vtep_id":1,
                        "vtep_source_ip":"10.200.10.30"
                    },
                ],
            },
        ],
        "peer_mgmt_ip":"",
        "peer_mgmt_port":"",

        "ha_sync_list": [
            {
                "ip": "1.1.1.1",
                "username": "admin",
                "password": "a10"
            }
        ]
    },
}

# Define a list of scheduler classes, which is how we pick which appliance we will
# put a given LB onto.  Any python class can be listed, as long as it conforms
# to the abstract interface defined in XXX.
# One fo the default schedlers will also spawn a nova instance.
# One will restrict by tenancy.
# These function similarly to nova filters.

providers = {
    'default': {
        'devices': devices,
        'scheduler': [ 'a10_neutron_lbaas.scheduler.ConsistentHash' ],
        'plumbing_hooks': blah,
        'neutron_hooks': blah
    }
    'vthunder': {
        'devices': None,
        'nova_user': 'service',
        'nova_password': 'password'
        'nova_tenant': 'service'
        'scheduler': [
            'a10_neutron_lbaas.scheduler.NovaSpawn',
            'a10_neutron_lbaas.scheduler.ConsistentHash'
        ],
    },
    'vthunder-inside-tenant': {
        'devices': None,
        'nova_user': 'service',
        'nova_password': 'password'
        'scheduler': [
            'a10_neutron_lbaas.scheduler.NovaSpawnInTenantSpace',
            'a10_neutron_lbaas.scheduler.ConsistentHash'
        ],
    },
    'other': {
        'scheduler': blah,
        'plumbing_hooks': blah,
        'neutron_hooks': blah
    }
    'vxlan-vtep': {
        'scheduler': blah,
        'plumbing_hooks': blah,
        'neutron_hooks': blah
        },
    default: hardware
}
