Device Instance API
====================

Device Instances
------------

Create
^^^^^^

.. http:post:: /v2.0/a10_device_instances

   Create a new :ref:`device instance <deviceinstance>`.

    When specifying networks, the management interface for the device is specified as the first member of the 'networks' collection.

   **Example request**:

   .. sourcecode:: http

        POST /v2.0/a10_device_instance HTTP/1.1
        Content-Type: application/json
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

        {
          "a10_device_instance": {
            "name": "mydevice",
            "description": "My vThunder device",
            "username": "a10user",
            "password": "a10password",
            "api_version": 3.0,
            "protocol": "HTTPS",
            "port": 443,
            "networks": ['mgmt-net', 'lb-net', 'member-net'],
            "image": "a10-vThunder-4.1.0",
            "flavor": "vthunder.min",
          }
        }

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 201 Created
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-381eb19f-49e1-4c8b-a979-8e59a2d19c61

        { 
          "a10_device_instance": {
            "id": "c131cb42-072a-4c3f-9d2d-89ee76d407a5"
            "tenant_id": "d9af4153807145e0ba232b02f6ab9aeb",
            "name": "mydevice",
            "description": "My vThunder device",
            "host": "10.10.10.103",
            "username": "a10user",
            "api_version": 3.0,
            "protocol": "https",
            "port": 443,
            "nova_instance_id": "8702583f-5994-4cb9-86fe-d23a49c2be61"            
          }
        }

   :<json string tenant_id: Owner openstack tenant/project id. (optional)
   :<json string name: Name for the device instance
   :<json string description: Optional description
   :<json string host: The management IP address of the device instance.
   :<json string username: Username for AXAPI authentication
   :<json float api_version: AXAPI Version (2.1 for 2.7.x devices, 3.0 for 4.x devices)
   :<json string protocol: Protocol to use when interacting with AXAPI (HTTP or HTTPS)
   :<json integer port: Port number to use when interacting with AXAPI (HTTP or HTTPS)
   :<json string nova_instance_id: Unique ID from Nova identifying the vThunder instance

   :statuscode 201:
   :statuscode 400:
   :statuscode 401:


Update
^^^^^^

.. http:put:: /v2.0/a10_device_instances/(id)

   Update a device instance by ID
   Once a device has been created, the only properties that can be updated are those not required for device instantiation.
   Device names, descriptions, and authentication information can be modified. Other properties such as the image used and networks attached
     can only be specified during creation.

   **Example request**:

   .. sourcecode:: http

        PUT /v2.0/a10_device_instances/00cfb9d9-9c84-40a1-a7b4-3da250e1a641.json HTTP/1.1
        Content-Type: application/json
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567
        {
          "a10_device_instance": {
            "name": "mydevice_newname", 
            "description": "Updated description",
            "username": "newuser",
            "password": "secret",
            "protocol": "HTTP",
            "port": 80
            }
        }

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-ca48bc5c-1c0e-4461-bf8c-ed0a7a1ee05f

        {
          "a10_device_instance": {
            "name": "mydevice_newname", 
            "description": "Updated description",
            "username": "newuser",
            "protocol": "HTTP",
            "port": 80
            }

        }

   :param id:

   :statuscode 200:
   :statuscode 400:
   :statuscode 401:
   :statuscode 404:


Get
^^^

.. http:get:: /v2.0/a10_device_instances/(id)

   Get a device instance by id.
   NOTE: Sensitive authentication information is not listed by this service.

   **Example request**:

   .. sourcecode:: http

        GET /v2.0/a10_device_instances/00cfb9d9-9c84-40a1-a7b4-3da250e1a641.json HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-e2c649aa-b7a1-49ee-adfc-d253c83b1b2c

        {
            "a10_device_instance": {
                "username": "admin", 
                "protocol": "https", 
                "name": "myname", 
                "tenant_id": "62941921b1194c5dba2d0c558ba29f5a", 
                "id": "00cfb9d9-9c84-40a1-a7b4-3da250e1a641", 
                "host": "10.10.10.103", 
                "nova_instance_id": "8702583f-5994-4cb9-86fe-d23a49c2be61", 
                "project_id": "62941921b1194c5dba2d0c558ba29f5a", 
                "port": 443, 
                "api_version": "3.0"
            }
        }

   :param id:

   :statuscode 200:
   :statuscode 401:
   :statuscode 404:


List
^^^^

.. http:get:: /v2.0/a10_device_instances

   List all device instances.

   **Example request**:

   .. sourcecode:: http

        GET /v2.0/a10_device_instances HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-df1dcc23-a8b3-4daa-8201-5b6927c1f20b

        {
            "a10_device_instances": [
                {
                    "username": "admin", 
                    "protocol": "https", 
                    "name": "myname", 
                    "tenant_id": "62941921b1194c5dba2d0c558ba29f5a", 
                    "id": "00cfb9d9-9c84-40a1-a7b4-3da250e1a641", 
                    "host": "172.24.4.11", 
                    "nova_instance_id": "26bf014b-ffc8-491f-9861-a56ad3e942c3", 
                    "project_id": "62941921b1194c5dba2d0c558ba29f5a", 
                    "port": 443, 
                    "api_version": "3.0"
                },
                {
                    "username": "admin",
                    "protocol": "https", 
                    "name": "device2", 
                    "tenant_id": "62941921b1194c5dba2d0c558ba29f5a", 
                    "id": "3406b011-dae3-46e9-82a8-0c35037cd2a5", 
                    "host": "172.24.4.12", 
                    "nova_instance_id": "dc3f20fc-5929-4191-bd9c-7d6fffe70f30", 
                    "project_id": "62941921b1194c5dba2d0c558ba29f5a", 
                    "port": 443, 
                    "api_version": "3.0"
                }
            ]
        }

   :statuscode 200:
   :statuscode 401:


Delete
^^^^^^

.. http:delete:: /v2.0/a10_device_instances/(id)

   Delete a device instance by ID

   **Example request**:

   .. sourcecode:: http

        DELETE /v2.0/a10_device_instances/3406b011-dae3-46e9-82a8-0c35037cd2a5 HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 204 No Content
        X-Openstack-Request-Id: req-23f140f4-21ad-40b8-9183-bff55c49b090

   :param id:

   :statuscode 204:
   :statuscode 401:
   :statuscode 404:

