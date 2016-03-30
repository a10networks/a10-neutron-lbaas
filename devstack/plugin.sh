#!/usr/bin/env bash

function install_a10 {
    if [ -n "$A10_DRIVER_GIT_URL" ]; then
        a="git+${A10_DRIVER_GIT_URL}#egg=a10_neutron_lbaas"
    else
        a="a10-neutron-lbaas"
    fi
    pip install -U $a
}

function configure_a10 {
    sudo mkdir -m 755 -p $A10_CONF_DIR
    safe_chown $STACK_USER $A10_CONF_DIR

    if [ -n "$A10_DEVICE_CONFIG" ]; then
        echo "$A10_DEVICE_CONFIG" > $A10_CONF_DIR/config.py
    else
        cat > $A10_CONF_DIR/config.py <<EOF
# For a complete list of configuration options, please refer to:
# https://github.com/a10networks/a10-neutron-lbaas/blob/master/a10_neutron_lbaas/etc/config.py

use_database = True
devices = {
    "host": "$A10_DEVICE_HOST",
    "port": $A10_DEVICE_PORT,
    "username": "$A10_DEVICE_USER",
    "password": "$A10_DEVICE_PASSWORD",
    "api_version": "$A10_DEVICE_AXAPI_VERSION",
}
EOF
    fi
}

function configure_a10_v1 {
    inicomment $NEUTRON_LBAAS_CONF service_providers service_provider
    iniadd $NEUTRON_LBAAS_CONF service_providers service_provider $A10_SERVICE_PROVIDER_V1
}

function configure_a10_v2 {
    inicomment $NEUTRON_LBAAS_CONF service_providers service_provider
    iniadd $NEUTRON_LBAAS_CONF service_providers service_provider $A10_SERVICE_PROVIDER_V2
}

# check for service enabled
if is_service_enabled a10-lbaasv1 -o is_service_enabled a10-lbaasv2; then

    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        # Set up system services
        # no-op
        :

    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        # Perform installation of service source
        echo_summary "Installing A10"
        install_a10

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        # Configure after the other layer 1 and 2 services have been configured
        echo_summary "Configuring A10"
        configure_a10

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        # Initialize and start the template service
        # no-op
        :
    fi

    if [[ "$1" == "unstack" ]]; then
        # Shut down template services
        # no-op
        :
    fi

    if [[ "$1" == "clean" ]]; then
        # Remove state and transient data
        # Remember clean.sh first calls unstack.sh
        # no-op
        :
    fi
fi

if is_service_enabled a10-lbaasv1; then
    if [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring A10 v1"
        configure_10_v1
    fi

elif is_service_enabled a10-lbaasv2; then
    if [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring A10 v2"
        configure_10_v2
    fi
fi
