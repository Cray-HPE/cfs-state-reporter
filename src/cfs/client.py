"""
This module is responsible for interacting with CFS in an reliable, authorized
fashion.
"""

import os
from cfs import CFSException
from . import PROTOCOL

import logging
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import subprocess

LOGGER = logging.getLogger('cfs.client')

TOKEN_DIR = "/etc/opt/cray/tokens/"
ACCESS_TOKEN_PATH = os.path.join(TOKEN_DIR, 'access')
REFRESH_TOKEN_PATH = os.path.join(TOKEN_DIR, 'refresh')

# Note: There is not a current process in place for what
# would otherwise update the access token, as stored in the
# ACCESS_TOKEN_PATH. Our assumption is that the token lifetime
# is sufficient for us to use it as part of multi-user.target
# right after a node reboots. The code is written to handle
# both kinds of files, should we ever need to extend this
# code to handle token refres operations.


def get_auth_token(path='/opt/cray/auth-utils/bin/get-auth-token'):
    if not os.getenv('SPIRE_AGENT_PATH'):
        os.environ['SPIRE_AGENT_PATH'] = '/usr/bin/cfs-state-reporter-spire-agent'
    try:
        out = subprocess.check_output([path], universal_newlines=True)
        out = out.rstrip('\n')
    except subprocess.CalledProcessError as e:
        LOGGER.error('Auth returned %d: %s' % (e.returncode, e.output))
        raise
    except Exception as e:
        LOGGER.error('Unexpected exception')
        LOGGER.error(e)
        raise
    return out


def requests_retry_session(retries=10, connect=10, backoff_factor=0.5,
                           status_forcelist=(500, 502, 503, 504),
                           session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount(PROTOCOL, adapter)
    session.headers.update({'Authorization': 'Bearer %s' % (get_auth_token())})
    return session
