import os
import logging

PROTOCOL = 'https'
API_GATEWAY_DNS_NAME = os.environ.get('API_GATEWAY_HOST', 'api-gw-service-nmn.local')
ENDPOINT = '%s://%s/apis/%s' % (PROTOCOL, API_GATEWAY_DNS_NAME, __name__.split('.')[-1])


class CFSException(Exception):
    """
    A Base class that all custom Exceptions from this
    project inherits from.
    """

# Setup project level loggging options
LOGGER = logging.getLogger(__name__)
