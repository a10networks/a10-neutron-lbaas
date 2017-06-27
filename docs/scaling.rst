Monitoring and Scaling
======================

.. _scaling-alarms:

Alarms
------

An alarm monitors the workers in a scaling group. It is triggered when a measurement, aggregated over all the workers over a time period, exceeds or is less than a threshold.

.. _scaling-alarm-aggregation:

Aggregation
^^^^^^^^^^^

``avg``
    The average (arithmetic mean) of all measurements made on all members during the period.

``max``
    The largest measured value on any member during the period

``min``
    The smallest measured value on any member during the period

``sum``
    The total value of all measurements made on all members during the period.
    By default the sampling rate is set to 1 measurement per seond.

.. _scaling-alarm-measurement:
.. _scaling-alarm-unit:

Measurements and Units
^^^^^^^^^^^^^^^^^^^^^^

``connections``
    The total number of open connections to all virtual servers on a member.
    Connections are measured in ``count``\ s.

``cpu``
    CPU use on data-plane CPUs. CPU use is measured in ``percentage``.

``interface``
    The number of connected interfaces. Interfaces are measured in ``count``\ s or ``percentage``.

``memory``
    The amount of memory consumed on the data-plane. Memory is measured in ``bytes`` or ``percentage``

.. _scaling-alarm-threshold:
.. _scaling-alarm-operator:

Threshold
^^^^^^^^^

The alarm is triggered if the aggregated measurement is greater than or equal-to (``>=``), greater than (``>``), less than or equal-to (``<=``), or less than (``<``) the threshold.

.. _scaling-alarm-period:
.. _scaling-alarm-period-unit:

Periods
^^^^^^^

The period measurements are aggregated over can be specified in ``minute``\ s, ``hour``\ s, or ``day``\ s.

.. _scaling-actions:

Actions
-------

An action is taken when an alarm is triggered. An action can be either to ``scale-in`` or ``scale-out`` by some number of workers.


``scale-in``
    Reduce the number of workers in the scaling group.

``scale-out``
    Increase the number of workers in the scaling group.

.. _scaling-policies:

Policies
--------

A policy determines when scaling actions should take place. It consists of a list of alarm, action pairs. When an alarm is triggered the corresponding action is taken. When multiple alarms would trigger reactions at the same time the first alarm in the list takes precedence.

After an alarm triggers an action no further actions will be taken until the policy's cooldown expires. Triggered reactions will not scale-in to fewer than the minimum instances or scale-out to more than the maximum instances (if there is a maximum).

.. _scaling-groups:

Scaling Groups
--------------

A scaling group is a scalable loadbalancer that can add or remove worker instances in response to load. Its scaling policy determines when new instances will be added by scaling out or removed by scaling in.

A scaling group consists of one direct server return switch master one or more workers. The master distributes incoming traffic amongst the workers, which respond directly to the client.

Scaling groups can be created by a scheduler in response to lbaas requests to create new loadbalancers.

.. _scaling-group-workers:

Scaling Group Workers
---------------------

A scaling group worker is a loadbalancer that handles some of the loadbalancing load in a scaling group.
