# Copyright 2020 Hewlett Packard Enterprise Development LP
import os
import logging

API_VERSION = 'v2'
PROTOCOL = 'https'
API_GATEWAY_DNS_NAME = os.environ.get('API_GATEWAY_HOST', 'api-gw-service-nmn.local')
ENDPOINT = '%s://%s/apis/%s/%s' % (PROTOCOL, API_GATEWAY_DNS_NAME,
                                   __name__.split('.')[-1], API_VERSION)


class CFSException(Exception):
    """
    A Base class that all custom Exceptions from this
    project inherits from.
    """

# Setup project level loggging options
LOGGER = logging.getLogger(__name__)
