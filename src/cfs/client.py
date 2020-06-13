"""
This module is responsible for interacting with CFS in an reliable, authorized
fashion.
"""

import os
from cfs import CFSException
from . import PROTOCOL
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

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


class TokenException(CFSException):
    """
    Issues arising from use of the access token that was stored on the system.
    """


def parse_path(path):
    """
    Reads the contents of a file; returns the contents of the file as
    a dictionary.

    The file in question is new-line deliminted with <key>=<value> format,
    similar to an ini file, but with some notable differences.
    """
    options = {}
    with open(path, 'r') as opened_file:
        for line in opened_file.readlines():
            ls = line.strip().split('=')
            if not ls:
                continue
            options[ls[0]] = ls[1]
    return options


def read_access_token():
    """
    Reads the access token from the local filesystem and returns it as
    a string.
    """
    try:
        return parse_path(ACCESS_TOKEN_PATH)['access_token']
    except (IOError, OSError) as token_error:
        raise TokenException(token_error)


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
    session.headers.update({'Authorization': 'Bearer %s' % (read_access_token())})
    return session
