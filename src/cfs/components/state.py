# Copyright 2020 Hewlett Packard Enterprise Development LP
"""
This is a client module to the CFS component state API. This allows
CFS to schedule configuration for nodes that have incorrect configuration
applied.

The primary use for this, is to allow nodes to indicate that they have
no configuration applied.
"""
import logging
import json
from requests.exceptions import HTTPError, ConnectionError
from urllib3.exceptions import MaxRetryError


from cfs.components import CFSComponentException
from cfs.components import ENDPOINT as COMPONENT_ENDPOINT
from cfs.client import requests_retry_session

LOGGER = logging.getLogger(__name__)


class UnknownComponent(CFSComponentException):
    """
    When we attempt to patch information on a component that doesn't exist.
    """


class UnrecognizedResponse(CFSComponentException):
    """
    CFS responded in an inconsistent fashion.
    """


def patch_component(component, properties, session=None):
    """
    For a given <component>, patch the component <properties> using
    the CFS API endpoint.
    """
    session = session or requests_retry_session()
    component_endpoint = '%s/%s' % (COMPONENT_ENDPOINT, component)
    session.patch(component_endpoint, json=properties)
    try:
        response = session.patch(component_endpoint, json=properties)
    except (ConnectionError, MaxRetryError) as ce:
        LOGGER.warning("Could not connect to CFS API service: %s" %(ce))
        raise CFSComponentException(ce)
    try:
        json_response = json.loads(response.text)
    except json.JSONDecodeError as jde:
        raise UnrecognizedResponse("CFS returned a non-json response: %s\n%s" % (response.text, jde))
    if response.status_code == 404:
        raise UnknownComponent(json_response['detail'])
    try:
        response.raise_for_status()
    except HTTPError as hpe:
        LOGGER.warning("Unexpected response from '%s':\n%s: %s", component_endpoint, response.status_code, response.text)
        raise CFSComponentException(hpe)


def mark_unconfigured(component, session=None):
    data = {'state': [], 'enabled': True}
    patch_component(component, data, session=session)

