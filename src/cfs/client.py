#
# MIT License
#
# (C) Copyright 2021-2022 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
"""
This module is responsible for interacting with CFS in a reliable, authorized
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
import time

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
# code to handle token refresh operations.


def get_auth_token(path='/opt/cray/auth-utils/bin/get-auth-token'):
    if not os.getenv('SPIRE_AGENT_PATH'):
        os.environ['SPIRE_AGENT_PATH'] = '/usr/bin/cfs-state-reporter-spire-agent'
    while True:
        try:
            out = subprocess.check_output([path], universal_newlines=True)
            out = out.rstrip('\n')
            return out
        except subprocess.CalledProcessError as e:
            LOGGER.error('Auth returned %d: %s' % (e.returncode, e.output))
        except Exception as e:
            LOGGER.error('Unexpected exception')
            LOGGER.error(e)
        LOGGER.info("Spire Token not yet available; retrying in a few seconds.")
        time.sleep(2)


class TimeoutHTTPAdapter(HTTPAdapter):
    """
    An HTTP Adapter that allows a session level timeout for both read and connect attributes.
    """
    def __init__(self, *args, **kwargs):
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None and hasattr(self, 'timeout'):
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)

def requests_retry_session(retries=10, connect=10, backoff_factor=0.5,
                           status_forcelist=(500, 502, 503, 504),
                           connect_timeout=3, read_timeout=10,
                           session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist
    )
    adapter = TimeoutHTTPAdapter(max_retries=retry, timeout=(connect_timeout, read_timeout))
    session.mount(PROTOCOL, adapter)
    session.headers.update({'Authorization': 'Bearer %s' % (get_auth_token())})
    return session
