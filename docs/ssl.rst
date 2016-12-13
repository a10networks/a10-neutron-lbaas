SSL Certificates
================

.. _certificates:

Certificates
------------

An SSL Certificate represents the certificate, password-protected private key, and any intermediary certificates associated with the certificate chain.

.. _certificates-datafields:

Certificate Data Fields
^^^^^^^^^^^^^^^^^^^^^^^

``cert_data``
    PEM-encoded representation of certificate.

``key_data``
    PEM-encoded representation of the certificate's private key.

``intermediate_data``
    PEM-encoded representation of supporting intermediary certificates.

``password``
    Password for private key


.. _certificate-bindings:

Certificate Bindings
--------------------

An SSL Certificate binding represents the relationship between a certificate and listener(s) the certificate is bound to.

.. _certificate-binding-datafields:

Certificate Binding Data Fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``certificate_id``
    The ID of the certificate being bound to the listener.

``listener_id``
    The ID of the listener

