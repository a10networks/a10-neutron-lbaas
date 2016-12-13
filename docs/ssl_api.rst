SSL Certificates API
====================

Certificates
------

Create
^^^^^^

.. http:post:: /v2.0/a10_certificates

   Create a new :ref:`certificate <certificates>`.

   **Example request**:

   .. sourcecode:: http

        POST /v2.0/a10_certificates HTTP/1.1
        Content-Type: application/json
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

        {
          "a10_certificate": {
            "name": "mycert",
            "key_data": "-----BEGIN PRIVATE KEY-----\nMIIEvgI...key data ...nYZS+TF2Pm8kMYULmXBYVKHf50\n-----END PRIVATE KEY-----\n", 
            "cert_data": "-----BEGIN CERTIFICATE-----\nMIID0T...cert data ...t\nqqENhqDhaCPEwLuglYOHVh\n-----END CERTIFICATE-----\n",
          }
        }

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 201 Created
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-381eb19f-49e1-4c8b-a979-8e59a2d19c61

        { 
          "a10_certificate": {
            "tenant_id": "d9af4153807145e0ba232b02f6ab9aeb", 
            "description": "", 
            "name": "mycert", 
            "id": "c131cb42-072a-4c3f-9d2d-89ee76d407a5"
          }
        }

   :<json string tenant_id: Owner openstack tenant/project id. (optional)
   :<json string name: A convenient name for the certificate.
   :<json string cert_data: The encoded certificate
   :<json string key_data: The encoded private key for the certificate
   :<json string intermediate_data: The encoded intermediary certificates needed to establish the certificate chain (optional)
   :<json string password: The password used to encrypt the private key (optional)
   :<json string description: A short description to be saved with the certificate. (optional)

   :>json string id:

   :statuscode 201:
   :statuscode 400:
   :statuscode 401:


Update
^^^^^^

.. http:put:: /v2.0/a10_certificates/(id)

   Update a certificate by ID
   Given the sensitive and semi-permanent nature of certificate data, only names and descriptions of certificates can be updated.
   To replace a certificate, create a new certificate and bind the listener to the new certificate.

   **Example request**:

   .. sourcecode:: http

        PUT /v2.0/a10_certificates/c131cb42-072a-4c3f-9d2d-89ee76d407a5 HTTP/1.1
        Content-Type: application/json
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

        {
          "a10_certificate": {
            "name": "mycert_newname", 
            "description": "My new description"
            }
        }

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-ca48bc5c-1c0e-4461-bf8c-ed0a7a1ee05f

        {
          "a10_certificate": {
            "tenant_id": "d9af4153807145e0ba232b02f6ab9aeb",
            "description": "My new description",
            "name": "mycert_newname",
            "id": "c131cb42-072a-4c3f-9d2d-89ee76d407a5"
          }
        }

   :param id:

   :statuscode 200:
   :statuscode 400:
   :statuscode 401:
   :statuscode 404:


Get
^^^

.. http:get:: /v2.0/a10_certificates/(id)

   Get a certificate by id.
   NOTE: Sensitive certificate data is not listed by the service.

   **Example request**:

   .. sourcecode:: http

        GET /v2.0/a10_certificates/c131cb42-072a-4c3f-9d2d-89ee76d407a5.json HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-e2c649aa-b7a1-49ee-adfc-d253c83b1b2c

        {
          "a10_certificate": {
            "tenant_id": "d9af4153807145e0ba232b02f6ab9aeb",
            "description": "",
            "name": "mycert",
            "id": "c131cb42-072a-4c3f-9d2d-89ee76d407a5"
          }
        }

   :param id:

   :statuscode 200:
   :statuscode 401:
   :statuscode 404:


List
^^^^

.. http:get:: /v2.0/a10_certificates

   List all certificates.

   **Example request**:

   .. sourcecode:: http

        GET /v2.0/a10_certificates HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-df1dcc23-a8b3-4daa-8201-5b6927c1f20b

        {
          "a10_certificates": [
            {
              "tenant_id": "d9af4153807145e0ba232b02f6ab9aeb",
              "description": "",
              "name": "mycert",
              "id": "c131cb42-072a-4c3f-9d2d-89ee76d407a5"
            },
            {
              "tenant_id": "d9af4153807145e0ba232b02f6ab9aeb",
              "description": "",
              "name": "myothercert",
              "id": "bf2f37f3-52f0-4301-9036-a9c014b4fa12"
            }
          ]
        }

   :statuscode 200:
   :statuscode 401:


Delete
^^^^^^

.. http:delete:: /v2.0/a10_certificates/(id)

   Delete a certificate by ID

   **Example request**:

   .. sourcecode:: http

        DELETE /v2.0/a10_certificates/c131cb42-072a-4c3f-9d2d-89ee76d407a5 HTTP/1.1
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
   :statuscode 409: Certificate is in use and cannot be deleted.


Certificate Bindings
-------

Create
^^^^^^

.. http:post:: /v2.0/a10_certificate_bindings

   Create a new :ref:`certificate/listener binding <certificate-bindings>`.

   **Example request**:

   .. sourcecode:: http

        POST /v2.0/a10_certificate_bindings HTTP/1.1
        Content-Type: application/json
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

        {
          "a10_certificate_binding": {
            "certificate_id": "c131cb42-072a-4c3f-9d2d-89ee76d407a5",
            "listener_id": "7a9f2bbd-eb9d-4ef6-b1ef-aefc71ea51c3"
          }
        }

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 201 Created
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-0c577c2e-bf2f-4d21-ae1d-88176c761106

        {
          "a10_certificate_binding": {
            "tenant_id": "d9af4153807145e0ba232b02f6ab9aeb",
            "certificate_name": "mycert",
            "listener_id": "7a9f2bbd-eb9d-4ef6-b1ef-aefc71ea51c3",
            "id": "31391770-c74e-4025-947a-78ff4827a291",
            "certificate_id": "c131cb42-072a-4c3f-9d2d-89ee76d407a5"
          }
        }

   :<json string tenant_id: Owner openstack tenant/project id. (optional)
   :<json string certificate_id: ID of Certificate object.
   :<json string listener_id: ID of LBaaS Listener object.

   :>json string id:

   :statuscode 201:
   :statuscode 400:
   :statuscode 401:


Get
^^^

.. http:get:: /v2.0/a10_certificate_bindings/(id)

   Get a certificate/listener binding by id.

   **Example request**:

   .. sourcecode:: http

        GET /v2.0/a10_certificate_bindings/31391770-c74e-4025-947a-78ff4827a291 HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-e0e61dce-2b05-4795-ac13-ee7f7076040e

        {
          "a10_certificate_binding": {
            "tenant_id": "d9af4153807145e0ba232b02f6ab9aeb",
            "certificate_name": "mycert",
            "listener_id": "7a9f2bbd-eb9d-4ef6-b1ef-aefc71ea51c3",
            "id": "31391770-c74e-4025-947a-78ff4827a291",
            "certificate_id": "c131cb42-072a-4c3f-9d2d-89ee76d407a5"
          },
        }

   :param id:

   :statuscode 200:
   :statuscode 401:
   :statuscode 404:


List
^^^^

.. http:get:: /v2.0/a10_certificate_bindings

   List all certificate/listener bindings.

   **Example request**:

   .. sourcecode:: http

        GET /v2.0/a10_certificate_bindings HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-d63b3b1f-89d2-418d-a311-630c4903ea64

      {
        "a10_certificate_bindings": [
          {
            "tenant_id": "d9af4153807145e0ba232b02f6ab9aeb",
            "certificate_name": "mycert",
            "listener_id": "7a9f2bbd-eb9d-4ef6-b1ef-aefc71ea51c3",
            "id": "31391770-c74e-4025-947a-78ff4827a291",
            "certificate_id": "c131cb42-072a-4c3f-9d2d-89ee76d407a5"
          },
          {
            "tenant_id": "d9af4153807145e0ba232b02f6ab9aeb",
            "certificate_name": "myothercert",
            "listener_id": "a4ebcf04-9e43-4cea-81f8-e9d677c07644",
            "id": "27e57b77-18a0-4231-8e7d-d1a59f911bf4",
            "certificate_id": "bf2f37f3-52f0-4301-9036-a9c014b4fa12"
          }
        ]
      }

   :statuscode 200:
   :statuscode 401:


Delete
^^^^^^

.. http:delete:: /v2.0/a10_certificate_binding/(id)

   Delete a certificate/listener binding by id.

   **Example request**:

   .. sourcecode:: http

        DELETE /v2.0/a10_certificate_bindings/31391770-c74e-4025-947a-78ff4827a291 HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 204 No Content
        X-Openstack-Request-Id: req-1293c119-1f79-4fc5-8f03-b713c33fada4

   :param id:

   :statuscode 204:
   :statuscode 401:
   :statuscode 404:
