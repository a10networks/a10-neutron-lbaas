Scaling API
===========

Alarms
------

Create
^^^^^^

.. http:post:: /v2.0/a10_scaling_alarms

   Create a new :ref:`alarm <scaling-alarms>`.

   **Example request**:

   .. sourcecode:: http

        POST /v2.0/a10_scaling_alarms HTTP/1.1
        Content-Type: application/json
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

        {
          "a10_scaling_alarm": {
            "period_unit": "minute",
            "unit": "percentage",
            "operator": ">=",
            "measurement": "cpu",
            "threshold": "80",
            "aggregation": "avg",
            "period": "5",
            "name": "cpu-high"
          }
        }

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 201 Created
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-381eb19f-49e1-4c8b-a979-8e59a2d19c61

        {
          "a10_scaling_alarm": {
            "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
            "name": "cpu-high",
            "period_unit": "minute",
            "description": "",
            "period": 5,
            "aggregation": "avg",
            "operator": ">=",
            "measurement": "cpu",
            "threshold": 80,
            "id": "824199ac-25d5-45ac-b62e-e1f9585fd858",
            "unit": "percentage"
          }
        }

   :<json string tenant_id: Owner openstack tenant/project id. (optional)
   :<json string name: A convenient name. (optional)
   :<json string description: A short description to be saved with the object. (optional)

   :<json string aggregation:

        How to :ref:`aggregate measurements <scaling-alarm-aggregation>` across members and over the period.
        One of ``avg``, ``min``, ``max``, or ``sum``.

   :<json string measurement:

        What :ref:`measurement <scaling-alarm-measurement>` to aggregate for the alarm.
        One of ``connections``, ``cpu``, ``interface``, or ``memory``.

   :<json string operator:

       How to compare the aggregated measurement to the threshold.
       The :ref:`operator <scaling-alarm-operator>` is one of ``>``, ``>=``, ``<=``, or ``<``.

   :<json number threshold:

       The :ref:`threshold <scaling-alarm-threshold>` at which the alarm triggers.

   :<json string unit:

       The :ref:`unit <scaling-alarm-unit>` the measurement and theshold are in.
       One of ``bytes``, ``count``, or ``percentage``.

   :<json string period:

       What :ref:`time period <scaling-alarm-period>` the measurements are aggregated over.

   :<json string period_unit:

       What :ref:`unit of time <scaling-alarm-period-unit>` the time period is measured in.
       One of ``minute``, ``hour``, or ``day``.

   :>json string id:

   :statuscode 201:
   :statuscode 400:
   :statuscode 401:


Update
^^^^^^

.. http:put:: /v2.0/a10_scaling_alarms/(id)

   Update an alarm by id.
   Update can be passed any of the arguments to :http:post:`/v2.0/a10_scaling_alarms` except for ``tenant_id``.

   **Example request**:

   .. sourcecode:: http

        PUT /v2.0/a10_scaling_alarms/824199ac-25d5-45ac-b62e-e1f9585fd858 HTTP/1.1
        Content-Type: application/json
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

        {
          "a10_scaling_alarm": {
            "threshold": "85"
          }
        }

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-ca48bc5c-1c0e-4461-bf8c-ed0a7a1ee05f

        {
          "a10_scaling_alarm": {
            "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
            "name": "cpu-high",
            "period_unit": "minute",
            "description": "",
            "period": 5,
            "aggregation": "avg",
            "operator": ">=",
            "measurement": "cpu",
            "threshold": 85,
            "id": "824199ac-25d5-45ac-b62e-e1f9585fd858",
            "unit": "percentage"
          }
        }

   :param id:

   :statuscode 200:
   :statuscode 400:
   :statuscode 401:
   :statuscode 404:


Get
^^^

.. http:get:: /v2.0/a10_scaling_alarms/(id)

   Get an alarm by id.

   **Example request**:

   .. sourcecode:: http

        GET /v2.0/a10_scaling_alarms/824199ac-25d5-45ac-b62e-e1f9585fd858 HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-e2c649aa-b7a1-49ee-adfc-d253c83b1b2c

        {
          "a10_scaling_alarm": {
            "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
            "name": "cpu-high",
            "period_unit": "minute",
            "description": "",
            "period": 5,
            "aggregation": "avg",
            "operator": ">=",
            "measurement": "cpu",
            "threshold": 85,
            "id": "824199ac-25d5-45ac-b62e-e1f9585fd858",
            "unit": "percentage"
          }
        }

   :param id:

   :statuscode 200:
   :statuscode 401:
   :statuscode 404:


List
^^^^

.. http:get:: /v2.0/a10_scaling_alarms

   List all alarms.

   **Example request**:

   .. sourcecode:: http

        GET /v2.0/a10_scaling_alarms HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-df1dcc23-a8b3-4daa-8201-5b6927c1f20b

        {
          "a10_scaling_alarms": [
            {
              "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
              "name": "cpu-high",
              "period_unit": "minute",
              "description": "",
              "period": 5,
              "aggregation": "avg",
              "operator": ">=",
              "measurement": "cpu",
              "threshold": 80,
              "id": "51429291-7d6c-41eb-9f4c-41a4315a4071",
              "unit": "percentage"
            },
            {
              "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
              "name": "connections-low",
              "period_unit": "hour",
              "description": "",
              "period": 1,
              "aggregation": "max",
              "operator": "<",
              "measurement": "connections",
              "threshold": 500,
              "id": "ea9c6a5b-d320-4fdf-aaa8-622302ca0848",
              "unit": "count"
            }
          ]
        }

   :statuscode 200:
   :statuscode 401:


Delete
^^^^^^

.. http:delete:: /v2.0/a10_scaling_alarms/(id)

   Delete an alarm by id.

   **Example request**:

   .. sourcecode:: http

        DELETE /v2.0/a10_scaling_alarms/824199ac-25d5-45ac-b62e-e1f9585fd858 HTTP/1.1
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
   :statuscode 409: The alarm is in use as part of a :ref:`scaling policy <scaling-policies>`\ 's reaction.


Actions
-------

Create
^^^^^^

.. http:post:: /v2.0/a10_scaling_actions

   Create a new :ref:`action <scaling-actions>`.

   **Example request**:

   .. sourcecode:: http

        POST /v2.0/a10_scaling_actions HTTP/1.1
        Content-Type: application/json
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

        {
          "a10_scaling_action": {
            "name": "scale-up",
            "amount": "2",
            "action": "scale-out"
          }
        }

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 201 Created
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-0c577c2e-bf2f-4d21-ae1d-88176c761106

        {
          "a10_scaling_action": {
            "name": "scale-up",
            "id": "e1ce7966-2f19-4cf1-810b-fff0da30d9b2",
            "action": "scale-out",
            "amount": 2,
            "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
            "description": ""
          }
        }

   :<json string tenant_id: Owner openstack tenant/project id. (optional)
   :<json string name: A convenient name. (optional)
   :<json string description: A short description to be saved with the object. (optional)

   :<json string action:

        One of ``scale-in`` or ``scale-out``.

   :<json number amount:

        The number of workers to scale in or out by.

   :>json string id:

   :statuscode 201:
   :statuscode 400:
   :statuscode 401:


Update
^^^^^^

.. http:put:: /v2.0/a10_scaling_actions/(id)

   Update an action by id.
   Update can be passed any of the arguments to :http:post:`/v2.0/a10_scaling_actions` except for ``tenant_id``.

   **Example request**:

   .. sourcecode:: http

        PUT /v2.0/a10_scaling_actions/e1ce7966-2f19-4cf1-810b-fff0da30d9b2 HTTP/1.1
        Content-Type: application/json
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

        {
          "a10_scaling_action": {
            "amount": "3"
          }
        }

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-885d46a1-98c3-46cd-8028-2e2610733ac9

        {
          "a10_scaling_action": {
            "name": "scale-up",
            "id": "e1ce7966-2f19-4cf1-810b-fff0da30d9b2",
            "action": "scale-out",
            "amount": 3,
            "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
            "description": ""
          }
        }

   :param id:

   :statuscode 200:
   :statuscode 400:
   :statuscode 401:
   :statuscode 404:


Get
^^^

.. http:get:: /v2.0/a10_scaling_actions/(id)

   Get an action by id.

   **Example request**:

   .. sourcecode:: http

        GET /v2.0/a10_scaling_actions/e1ce7966-2f19-4cf1-810b-fff0da30d9b2 HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-e0e61dce-2b05-4795-ac13-ee7f7076040e

        {
          "a10_scaling_action": {
            "name": "scale-up",
            "id": "e1ce7966-2f19-4cf1-810b-fff0da30d9b2",
            "action": "scale-out",
            "amount": 3,
            "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
            "description": ""
          }
        }


   :param id:

   :statuscode 200:
   :statuscode 401:
   :statuscode 404:


List
^^^^

.. http:get:: /v2.0/a10_scaling_actions

   List all actions.

   **Example request**:

   .. sourcecode:: http

        GET /v2.0/a10_scaling_actions HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-d63b3b1f-89d2-418d-a311-630c4903ea64

        {
          "a10_scaling_actions": [
            {
              "name": "scale-down",
              "id": "1e1b7dd1-8797-4a7e-bddf-c7a145569c1a",
              "action": "scale-in",
              "amount": 1,
              "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
              "description": ""
            },
            {
              "name": "scale-up",
              "id": "e1ce7966-2f19-4cf1-810b-fff0da30d9b2",
              "action": "scale-out",
              "amount": 3,
              "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
              "description": ""
            }
          ]
        }

   :statuscode 200:
   :statuscode 401:


Delete
^^^^^^

.. http:delete:: /v2.0/a10_scaling_actions/(id)

   Delete an alarm by id.

   **Example request**:

   .. sourcecode:: http

        DELETE /v2.0/a10_scaling_actions/e1ce7966-2f19-4cf1-810b-fff0da30d9b2 HTTP/1.1
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
   :statuscode 409: The action is in use as part of a :ref:`scaling policy <scaling-policies>`\ 's reaction.


Policies
--------

Create
^^^^^^

.. http:post:: /v2.0/a10_scaling_policies

   Create a new :ref:`scaling policy <scaling-policies>`.

   **Example request**:

   .. sourcecode:: http

        POST /v2.0/a10_scaling_policies HTTP/1.1
        Content-Type: application/json
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

        {
          "a10_scaling_policy": {
            "max_instances": "20",
            "name": "up-fast-bounded",
            "cooldown": "300",
            "reactions": [
              {
                "action_id": "e1ce7966-2f19-4cf1-810b-fff0da30d9b2",
                "alarm_id": "51429291-7d6c-41eb-9f4c-41a4315a4071"
              },
              {
                "action_id": "1e1b7dd1-8797-4a7e-bddf-c7a145569c1a",
                "alarm_id": "ea9c6a5b-d320-4fdf-aaa8-622302ca0848"
              }
            ],
            "min_instances": "2"
          }
        }

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 201 Created
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-9e285515-e499-43ca-90aa-e97454aff53b

        {
          "a10_scaling_policy": {
            "name": "up-fast-bounded",
            "id": "d3b23a8e-359b-4279-af0b-4fe2dc4ce6bc",
            "cooldown": 300,
            "max_instances": 20,
            "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
            "min_instances": 2,
            "description": "",
            "reactions": [
              {
                "action_id": "e1ce7966-2f19-4cf1-810b-fff0da30d9b2",
                "alarm_id": "51429291-7d6c-41eb-9f4c-41a4315a4071"
              },
              {
                "action_id": "1e1b7dd1-8797-4a7e-bddf-c7a145569c1a",
                "alarm_id": "ea9c6a5b-d320-4fdf-aaa8-622302ca0848"
              }
            ]
          }
        }


   :<json string tenant_id: Owner openstack tenant/project id. (optional)
   :<json string name: A convenient name. (optional)
   :<json string description: A short description to be saved with the object. (optional)

   :<json number cooldown:

        Minimum time period in seconds between scaling actions.

   :<json array reactions:

       Reactions are pairs of an alarm and the action to take when the
       alarm is triggered.
       Each one is a dictionary with an ``"action_id"`` and an ``"alarm_id"``.
       If multiple alarms would be triggered simultaneously,
       the first one in the list takes precedence.

   :<json number min_instances:

        The minimum number of workers in the group. Must be greater than or equal to 1. (optional)

   :<json number max_instances:

        The maximum number of workers in the group or ``null``.
        Must be greater than or equal to ``min_instances``. (optional)

   :>json string id:

   :statuscode 201:
   :statuscode 400:
   :statuscode 401:


Update
^^^^^^

.. http:put:: /v2.0/a10_scaling_policies/(id)

   Update a policy by id.
   Update can be passed any of the arguments to :http:post:`/v2.0/a10_scaling_policies` except for ``tenant_id``.

   **Example request**:

   .. sourcecode:: http

        PUT /v2.0/a10_scaling_policies/d3b23a8e-359b-4279-af0b-4fe2dc4ce6bc HTTP/1.1
        Content-Type: application/json
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

        {
          "a10_scaling_policy": {
            "max_instances": null,
            "name": "up-fast"
          }
        }

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-2ed7b40f-cd1c-4261-9bfd-5dc4f8650328

        {
          "a10_scaling_policy": {
            "name": "up-fast",
            "id": "d3b23a8e-359b-4279-af0b-4fe2dc4ce6bc",
            "cooldown": 300,
            "max_instances": null,
            "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
            "min_instances": 2,
            "description": "",
            "reactions": [
              {
                "action_id": "e1ce7966-2f19-4cf1-810b-fff0da30d9b2",
                "alarm_id": "51429291-7d6c-41eb-9f4c-41a4315a4071"
              },
              {
                "action_id": "1e1b7dd1-8797-4a7e-bddf-c7a145569c1a",
                "alarm_id": "ea9c6a5b-d320-4fdf-aaa8-622302ca0848"
              }
            ]
          }
        }


   :param id:

   :statuscode 200:
   :statuscode 400:
   :statuscode 401:
   :statuscode 404:


Get
^^^

.. http:get:: /v2.0/a10_scaling_policies/(id)

   Get an alarm by id.

   **Example request**:

   .. sourcecode:: http

        GET /v2.0/a10_scaling_policies/d3b23a8e-359b-4279-af0b-4fe2dc4ce6bc HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-d3cd7156-0297-428a-b82f-0bc8a162aecc

        {
          "a10_scaling_policy": {
            "name": "up-fast",
            "id": "d3b23a8e-359b-4279-af0b-4fe2dc4ce6bc",
            "cooldown": 300,
            "max_instances": null,
            "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
            "min_instances": 2,
            "description": "",
            "reactions": [
              {
                "action_id": "e1ce7966-2f19-4cf1-810b-fff0da30d9b2",
                "alarm_id": "51429291-7d6c-41eb-9f4c-41a4315a4071"
              },
              {
                "action_id": "1e1b7dd1-8797-4a7e-bddf-c7a145569c1a",
                "alarm_id": "ea9c6a5b-d320-4fdf-aaa8-622302ca0848"
              }
            ]
          }
        }


   :param id:

   :statuscode 200:
   :statuscode 401:
   :statuscode 404:


List
^^^^

.. http:get:: /v2.0/a10_scaling_policies

   List all policies.

   **Example request**:

   .. sourcecode:: http

        GET /v2.0/a10_scaling_policies HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-34852647-155d-4737-bd7d-b3364a3dd9de

        {
          "a10_scaling_policies": [
            {
              "name": "up-fast",
              "id": "d3b23a8e-359b-4279-af0b-4fe2dc4ce6bc",
              "cooldown": 300,
              "max_instances": null,
              "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
              "min_instances": 2,
              "description": "",
              "reactions": [
                {
                  "action_id": "e1ce7966-2f19-4cf1-810b-fff0da30d9b2",
                  "alarm_id": "51429291-7d6c-41eb-9f4c-41a4315a4071"
                },
                {
                  "action_id": "1e1b7dd1-8797-4a7e-bddf-c7a145569c1a",
                  "alarm_id": "ea9c6a5b-d320-4fdf-aaa8-622302ca0848"
                }
              ]
            }
          ]
        }


   :statuscode 200:
   :statuscode 401:


Delete
^^^^^^

.. http:delete:: /v2.0/a10_scaling_policies/(id)

   Delete an alarm by id.

   **Example request**:

   .. sourcecode:: http

        DELETE /v2.0/a10_scaling_policies/d3b23a8e-359b-4279-af0b-4fe2dc4ce6bc HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 204 No Content
        X-Openstack-Request-Id: req-b4052d47-1b2e-4baa-8449-08fcab2b1742

   :param id:

   :statuscode 204:
   :statuscode 401:
   :statuscode 404:
   :statuscode 409: The policy is in use by a :ref:`scaling group <scaling-groups>`.


Scaling Groups
--------------

Scaling groups can be manipulated through the API, but will usually be managed automatically by a scheduler.

Create
^^^^^^

.. http:post:: /v2.0/a10_scaling_groups

   Create a new :ref:`scaling group <scaling-groups>`.

   **Example request**:

   .. sourcecode:: http

        POST /v2.0/a10_scaling_groups HTTP/1.1
        Content-Type: application/json
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

        {
          "a10_scaling_group": {
            "name": "sg1",
            "scaling_policy_id": "d3b23a8e-359b-4279-af0b-4fe2dc4ce6bc"
          }
        }

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 201 Created
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-c7c8c28b-d835-4b11-b8ca-f852d0deef3e

        {
          "a10_scaling_group": {
            "name": "sg1",
            "id": "2421007c-c13e-4135-b9a9-9bb41e29c336",
            "scaling_policy_id": "d3b23a8e-359b-4279-af0b-4fe2dc4ce6bc",
            "description": "",
            "tenant_id": "0ef49a3d333a4a6684194b278af5d62e"
          }
        }


   :<json string tenant_id: Owner openstack tenant/project id. (optional)
   :<json string name: A convenient name. (optional)
   :<json string description: A short description to be saved with the object. (optional)

   :<json string scaling_policy_id:

       The scaling policy to use to determine when to add or remove workers from this scaling group.
       The id of a policy or ``null``. (optional)

   :>json string id:

   :statuscode 201:
   :statuscode 400:
   :statuscode 401:


Update
^^^^^^

.. http:put:: /v2.0/a10_scaling_groups/(id)

   Update a scaling group.
   Update can be passed any of the arguments to :http:post:`/v2.0/a10_scaling_groups` except for ``tenant_id``.

   **Example request**:

   .. sourcecode:: http

        PUT /v2.0/a10_scaling_groups/2421007c-c13e-4135-b9a9-9bb41e29c336 HTTP/1.1
        Content-Type: application/json
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

        {
          "a10_scaling_group": {
            "scaling_policy_id": null
          }
        }

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-2354611b-2517-483b-add9-b8539ece8cf1

        {
          "a10_scaling_group": {
            "name": "sg1",
            "id": "2421007c-c13e-4135-b9a9-9bb41e29c336",
            "scaling_policy_id": null,
            "description": "",
            "tenant_id": "0ef49a3d333a4a6684194b278af5d62e"
          }
        }

   :param id:

   :statuscode 200:
   :statuscode 400:
   :statuscode 401:
   :statuscode 404:


Get
^^^

.. http:get:: /v2.0/a10_scaling_groups/(id)

   Get a scaling group by id.

   **Example request**:

   .. sourcecode:: http

        GET /v2.0/a10_scaling_groups/2421007c-c13e-4135-b9a9-9bb41e29c336 HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-5748b57e-c57e-49a1-9cc4-bb120185f46e

        {
          "a10_scaling_group": {
            "name": "sg1",
            "id": "2421007c-c13e-4135-b9a9-9bb41e29c336",
            "scaling_policy_id": "d3b23a8e-359b-4279-af0b-4fe2dc4ce6bc",
            "description": "",
            "tenant_id": "0ef49a3d333a4a6684194b278af5d62e"
          }
        }

   :param id:

   :statuscode 200:
   :statuscode 401:
   :statuscode 404:


List
^^^^

.. http:get:: /v2.0/a10_scaling_groups

   List all scaling groups.

   **Example request**:

   .. sourcecode:: http

        GET /v2.0/a10_scaling_groups HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-9ea713ac-1677-4f81-9745-4ed75fa15609

        {
          "a10_scaling_groups": [
            {
              "name": "sg1",
              "id": "2421007c-c13e-4135-b9a9-9bb41e29c336",
              "scaling_policy_id": "d3b23a8e-359b-4279-af0b-4fe2dc4ce6bc",
              "description": "",
              "tenant_id": "0ef49a3d333a4a6684194b278af5d62e"
            },
            {
              "name": "sg2",
              "id": "4d5e92bf-b009-48ea-b73a-d5146808f3aa",
              "scaling_policy_id": null,
              "description": "",
              "tenant_id": "0ef49a3d333a4a6684194b278af5d62e"
            }
          ]
        }

   :statuscode 200:
   :statuscode 401:


Delete
^^^^^^

.. http:delete:: /v2.0/a10_scaling_groups/(id)

   Delete an alarm by id.

   **Example request**:

   .. sourcecode:: http

        DELETE /v2.0/a10_scaling_groups/2421007c-c13e-4135-b9a9-9bb41e29c336 HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 204 No Content
        X-Openstack-Request-Id: req-abb3ba62-2c3f-4993-b5d8-82e155e6fd54

   :param id:

   :statuscode 204:
   :statuscode 401:
   :statuscode 404:
   :statuscode 409: The scaling group is in use by an lbaas loadbalancer or pool.


Scaling Group Workers
---------------------

Scaling group workers can be manipulated through the API, but will usually be managed automatically according to the scaling group’s policy.


Create
^^^^^^

.. http:post:: /v2.0/a10_scaling_group_workers

   Create a new :ref:`scaling group worker <scaling-group-workers>` for the specified scaling group.

   **Example request**:

   .. sourcecode:: http

        POST /v2.0/a10_scaling_group_workers HTTP/1.1
        Content-Type: application/json
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

        {
          "a10_scaling_group_worker": {
            "scaling_group_id": "2421007c-c13e-4135-b9a9-9bb41e29c336"
          }
        }


   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 201 Created
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-2ce153d2-ef90-4fc8-93c8-ec8daf5891f6

        {
          "a10_scaling_group_worker": {
            "name": "",
            "api_version": "2.1",
            "port": 443,
            "username": "admin",
            "protocol": "https",
            "description": "",
            "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
            "scaling_group_id": "2421007c-c13e-4135-b9a9-9bb41e29c336",
            "id": "ea46a2bf-4adc-4f1c-aaa6-5f29287b849a",
            "host": "10.90.100.38",
            "nova_instance_id": "88754b66-74f5-4ec2-8a4c-d18035abe0a3"
          }
        }


   :<json string tenant_id: Owner openstack tenant/project id. (optional)
   :<json string name: A convenient name. (optional)
   :<json string description: A short description to be saved with the object. (optional)

   :<json string scaling_group_id:

        The scaling group to add the worker to.

   :>json string id:

   :>json string host:

        Management IP address of the launched nova instance.

   :>json string protocol:

        AXAPI protocol. One of ``http`` or ``https``.

   :>json string port:

        AXAPI port.

   :>json string api_version:

        AXAPI version number. One of ``2.1`` or ``3.0``.

   :>json string username:

        AXAPI username

   :>json string nova_instance_id:

        Nova ID of the launched nova instance.

   :statuscode 201:
   :statuscode 400:
   :statuscode 401:


Update
^^^^^^

.. http:put:: /v2.0/a10_scaling_group_workers/(id)

   Update a scaling group worker.
   Update can be passed any of the arguments to or responses from :http:post:`/v2.0/a10_scaling_group_workers` except for ``id``, ``tenant_id``, ``scaling_group_id``, or ``nova_instance_id``.

   **Example request**:

   .. sourcecode:: http

        PUT /v2.0/a10_scaling_group_workers/ea46a2bf-4adc-4f1c-aaa6-5f29287b849a HTTP/1.1
        Content-Type: application/json
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

        {
          "a10_scaling_group_worker": {
            "name": "worker1"
          }
        }

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-333ed0a7-93f2-4b1d-bf26-6612d05f5683

        {
          "a10_scaling_group_worker": {
            "name": "worker1",
            "api_version": "2.1",
            "port": 443,
            "username": "admin",
            "protocol": "https",
            "description": "",
            "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
            "scaling_group_id": "2421007c-c13e-4135-b9a9-9bb41e29c336",
            "id": "ea46a2bf-4adc-4f1c-aaa6-5f29287b849a",
            "host": "10.90.100.38",
            "nova_instance_id": "88754b66-74f5-4ec2-8a4c-d18035abe0a3"
          }
        }


   :param id:

   :<json string password:

        AXAPI password.

   :statuscode 200:
   :statuscode 400:
   :statuscode 401:
   :statuscode 404:


Get
^^^

.. http:get:: /v2.0/a10_scaling_group_workers/(id)

   Get an alarm by id.

   **Example request**:

   .. sourcecode:: http

        GET /v2.0/a10_scaling_group_workers/ea46a2bf-4adc-4f1c-aaa6-5f29287b849a HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-e8a0077a-0e8c-48f0-a8c7-55f3b00e3dee

        {
          "a10_scaling_group_worker": {
            "name": "worker1",
            "api_version": "2.1",
            "port": 443,
            "username": "admin",
            "protocol": "https",
            "description": "",
            "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
            "scaling_group_id": "2421007c-c13e-4135-b9a9-9bb41e29c336",
            "id": "ea46a2bf-4adc-4f1c-aaa6-5f29287b849a",
            "host": "10.90.100.38",
            "nova_instance_id": "88754b66-74f5-4ec2-8a4c-d18035abe0a3"
          }
        }

   :param id:

   :statuscode 200:
   :statuscode 401:
   :statuscode 404:


List
^^^^

.. http:get:: /v2.0/a10_scaling_group_workers

   List all alarms.

   **Example request**:

   .. sourcecode:: http

        GET /v2.0/a10_scaling_group_workers HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json; charset=UTF-8
        X-Openstack-Request-Id: req-8b63a3a0-6865-4381-bdf0-fd0b0c8793ab

        {
          "a10_scaling_group_workers": [
            {
              "name": "",
              "api_version": "2.1",
              "port": 443,
              "username": "admin",
              "protocol": "https",
              "description": "",
              "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
              "scaling_group_id": "2421007c-c13e-4135-b9a9-9bb41e29c336",
              "id": "504f6073-a792-4e2f-a6bf-f5c14970c45a",
              "host": "10.90.100.41",
              "nova_instance_id": "6580079b-7811-4ebf-9550-a114a5adaf78"
            },
            {
              "name": "worker1",
              "api_version": "2.1",
              "port": 443,
              "username": "admin",
              "protocol": "https",
              "description": "",
              "tenant_id": "0ef49a3d333a4a6684194b278af5d62e",
              "scaling_group_id": "2421007c-c13e-4135-b9a9-9bb41e29c336",
              "id": "ea46a2bf-4adc-4f1c-aaa6-5f29287b849a",
              "host": "10.90.100.38",
              "nova_instance_id": "88754b66-74f5-4ec2-8a4c-d18035abe0a3"
            }
          ]
        }


   :statuscode 200:
   :statuscode 401:


Delete
^^^^^^

.. http:delete:: /v2.0/a10_scaling_group_workers/(id)

   Delete an alarm by id.

   **Example request**:

   .. sourcecode:: http

        DELETE /v2.0/a10_scaling_group_workers/ea46a2bf-4adc-4f1c-aaa6-5f29287b849a HTTP/1.1
        Accept: application/json
        X-Auth-Token: {SHA1}0123456789ABCDEF0123456789ABCDEF01234567

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 204 No Content
        X-Openstack-Request-Id: req-b1a430af-97ad-4477-aebe-c91c6069134e

   :param id:

   :statuscode 204:
   :statuscode 401:
   :statuscode 404:
