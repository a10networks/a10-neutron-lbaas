Command Line Client
===================


Installation
------------

Install the `neutron command line client <http://docs.openstack.org/developer/python-neutronclient/>`_ ::

    pip install python-neutronclient

Install the A10 Openstack command line client extension ::

    pip install a10-openstack


Scaling
-------

Common Options
^^^^^^^^^^^^^^

All scaling objects can be given a name for convenience and a short description for documentation.

.. program:: neutron

.. option:: --name <name>

   A convenient name. If unique, the name can be used in place of the object's id when an id is needed.

.. option:: --description <description>

   A short description to be saved with the object.


Alarms
^^^^^^

Create
""""""

.. program:: a10-scaling-alarm

.. option:: a10-scaling-alarm-create <name>

   Create a new :ref:`alarm <scaling-alarms>`.

   Examples::

       neutron a10-scaling-alarm-create cpu-high \
           --aggregation avg \
           --measurement cpu \
           --operator '>=' \
           --threshold 80 \
           --unit percentage \
           --period 5 \
           --period_unit minute

       neutron a10-scaling-alarm-create connections-low \
           --aggregation max \
           --measurement connections \
           --operator '<' \
           --threshold 500 \
           --unit count \
           --period 1 \
           --period_unit hour

.. option:: --aggregation <aggregation>

   How to :ref:`aggregate measurements <scaling-alarm-aggregation>` across members and over the period.
   One of ``avg``, ``min``, ``max``, or ``sum``.

.. option:: --measurement <measurement>

   What :ref:`measurement <scaling-alarm-measurement>` to aggregate for the alarm.
   One of ``connections``, ``cpu``, ``interface``, or ``memory``.

.. option:: --operator <operator>

   How to compare the aggregated measurement to the threshold.
   The :ref:`operator <scaling-alarm-operator>` is one of ``>``, ``>=``, ``<=``, or ``<``.

.. option:: --threshold <threshold>

   The :ref:`threshold <scaling-alarm-threshold>` at which the alarm triggers.

.. option:: --unit <unit>

   The :ref:`unit <scaling-alarm-unit>` the measurement and theshold are in.
   One of ``bytes``, ``count``, or ``percentage``.

.. option:: --period <period>

   What :ref:`time period <scaling-alarm-period>` the measurements are aggregated over.

.. option:: --period-unit <period_unit>

   What :ref:`unit of time <scaling-alarm-period-unit>` the time period is measured in.
   One of ``minute``, ``hour``, or ``day``.

Update
""""""

.. option:: a10-scaling-alarm-update <name_or_id>

   Update an alarm by name or id.
   Update can be passed any of the arguments to :option:`a10-scaling-alarm-create` or a :option:`--name <neutron --name>`.

   Examples::

       neutron a10-scaling-alarm-update cpu-high --threshold 85
       neutron a10-scaling-alarm-update cpu-high \
           --name cpu-really-high \
           --aggregation max

Show
""""

.. option:: a10-scaling-alarm-show <name_or_id>

   Show an alarm by name or id.

   Example::

       neutron a10-scaling-alarm-show cpu-high

List
""""

.. option:: a10-scaling-alarm-list

   List all alarms.

   Example::

       neutron a10-scaling-alarm-list

Delete
""""""

.. option:: a10-scaling-alarm-delete <name_or_id>

   Delete an alarm by name or id.

   Example::

       neutron a10-scaling-alarm-delete cpu-high


Actions
^^^^^^^

Create
""""""

.. program:: a10-scaling-action

.. option:: a10-scaling-action-create <name>

   Create a new :ref:`action <scaling-actions>`.

   Examples::

       neutron a10-scaling-action-create scale-up \
           --action scale-out --amount 2
       neutron a10-scaling-action-create scale-down \
           --action scale-in --amount 1

.. option:: --action <action>

   One of ``scale-in`` or ``scale-out``.

.. option:: --amount <amount>

   The number of workers to scale in or out by.

Update
""""""

.. option:: a10-scaling-action-update <name_or_id>

   Update an action by name or id.
   Update can be passed any of the arguments to :option:`a10-scaling-action-create` or a :option:`--name <neutron --name>`.

   Example::

       neutron a10-scaling-action-update scale-out --amount 3

Show
""""

.. option:: a10-scaling-action-show <name_or_id>

   Show an action by name or id.

   Example::

       neutron a10-scaling-action-show scale-out

List
""""

.. option:: a10-scaling-action-list

   List all actions.

   Example::

       neutron a10-scaling-action-list

Delete
""""""

.. option:: a10-scaling-action-delete <name_or_id>

   Delete an action by name or id.

   Example::

       neutron a10-scaling-action-delete scale-out


Policies
^^^^^^^^

Create
""""""

.. program:: a10-scaling-policy

.. option:: a10-scaling-policy-create <name>

   Create a new :ref:`scaling policy <scaling-policies>`.

   Examples::

       neutron a10-scaling-policy-create up-fast \
           --cooldown 300 \
           --reactions \
               alarm=cpu-high,action=scale-up \
               alarm=connections-low,action=scale-down

       neutron a10-scaling-policy-create up-fast-bounded \
           --cooldown 300 \
           --reactions \
               alarm=cpu-high,action=scale-up \
               alarm=connections-low,action=scale-down \
           --min-instances 2 \
           --max-instances 20

.. option:: --cooldown <cooldown>

   Minimum time period in seconds between scaling actions.

.. option:: --reactions <reaction>...

   Reactions are pairs of an alarm and the action to take when the
   alarm is triggered.
   Each one is written as `alarm=<alarm>.action=<action>`.
   The alarm is the name or id of an alarm created with :option:`a10-scaling-alarm-create <a10-scaling-alarm a10-scaling-alarm-create>`.
   The action is the name or id of an action created with :option:`a10-scaling-action-create <a10-scaling-action a10-scaling-action-create>`.
   If multiple alarms would be triggered simultaneously,
   the first one in the list takes precedence.

.. option:: --min-instances <reactions>

   The minimum number of workers in the group. Must be greater than or equal to 1.

.. option:: --max-instances <max-instances>

   The maximum number of workers in the group.
   Must be greater than or equal to :option:`--min-instances`.

.. option:: --no-max-instances

   The policy won't restrict the maximum number of workers in the group.
   Removes a maximum set by :option:`--max-instances`.

Update
""""""

.. option:: a10-scaling-policy-update <name_or_id>

   Update a policy by name or id.
   Update can be passed any of the arguments to :option:`a10-scaling-policy-create` or a :option:`--name <neutron --name>`.

   Examples::

       neutron a10-scaling-policy-update up-fast-bounded \
           --name up-fast-unbounded \
           --no-max-instances

       neutron a10-scaling-polciy-update up-fast \
           alarm=cpu-high,action=scale-up \
           alarm=connections-high,action=scale-up \
           alarm=connections-low,action=scale-down

Show
""""

.. option:: a10-scaling-policy-show <name_or_id>

   Show a policy by name or id.

   Example::

       neutron a10-scaling-policy-show up-fast

List
""""

.. option:: a10-scaling-policy-list

   List all policies.

   Example::

       neutron a10-scaling-policy-list

Delete
""""""

.. option:: a10-scaling-policy-delete <name_or_id>

   Delete a policy by name or id.

   Example::

       neutron a10-scaling-policy-delete up-fast


Scaling Groups
^^^^^^^^^^^^^^

Scaling groups can be manually manipulated through the CLI, but will usually be managed automatically by a scheduler.

Create
""""""

.. program:: a10-scaling-group

.. option:: a10-scaling-group-create <name>

   Create a new :ref:`scaling group <scaling-groups>`.

   Examples::

       neutron a10-scaling-group-create sg1
       neutron a10-scaling-group-create sg2 --scaling-policy fast-up

.. option:: --scaling-policy <scaling-policy>

   The scaling policy to use to determine when to add or remove workers from this scaling group.
   Must be the name or id of a policy created with :option:`a10-scaling-policy-create <a10-scaling-policy a10-scaling-policy-create>`.


.. option:: --no-scaling-policy

   Removes a scaling policy set by :option:`--scaling-policy`.

Update
""""""

.. option:: a10-scaling-group-update <name_or_id>

   Update a scaling group by name or id.
   Update can be passed any of the arguments to :option:`a10-scaling-group-create` or a :option:`--name <neutron --name>`.

   Examples::

       neutron a10-scaling-group-update sg1 --name more-descriptive-name
       neutron a10-scaling-group-update sg2 --no-scaling-policy

Show
""""

.. option:: a10-scaling-group-show <name_or_id>

   Show a scaling group by name or id.

   Example::

       neutron a10-scaling-group-show sg1

List
""""

.. option:: a10-scaling-group-list

   List all scaling groups.

   Example::

       neutron a10-scaling-group-delete sg1

Delete
""""""

.. option:: a10-scaling-group-delete <name_or_id>

   Delete a scaling group by name or id.

   Example::

       neutron a10-scaling-group-delete sg1


Scaling Group Workers
^^^^^^^^^^^^^^^^^^^^^

Scaling groups workers can be manually manipulated through the CLI, but will usually be managed automatically according to the scaling group's policy.

Create
""""""

.. program:: a10-scaling-group-worker

.. option:: a10-scaling-group-worker-create <scaling-group>

   Create a new :ref:`scaling group worker <scaling-group-workers>` for the specified scaling group.
   The scaling-group must be the name or id ofa scaling-group created with :option:`a10-scaling-group-create <a10-scaling-group a10-scaling-group-create>`.

   Examples::

       neutron a10-scaling-group-worker-create sg1
       neutron a10-scaling-group-worker-create sg1 --name manually-created-worker


Show
""""

.. option:: a10-scaling-group-worker-show <name_or_id>

   Show a scaling group worker by name or id.

   Example::

       neutron a10-scaling-group-worker-show manually-created-worker

List
""""

.. option:: a10-scaling-group-worker-list

   List all scaling groups workers.

   Example::

       neutron a10-scaling-group-worker-list

Delete
""""""

.. option:: a10-scaling-group-worker-delete <name_or_id>

   Delete a scaling group worker by name or id.

   Example::

       neutron a10-scaling-group-worker-delete manually-created-worker
