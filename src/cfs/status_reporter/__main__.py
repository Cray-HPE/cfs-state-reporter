#
# MIT License
#
# (C) Copyright 2020-2022 Hewlett Packard Enterprise Development LP
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
import logging
import sys
import os
from time import sleep
from logging.handlers import RotatingFileHandler

from cfs.client import requests_retry_session
from cfs.node_identity import read_identity
from cfs.components.state import mark_unconfigured, CFSComponentException, UnknownComponent
from cfsssh.setup.client.run import main as cfsssh_setup_main

# Configure Root Level Logging options when invoked through __main__;
# This allows the whole project to log from their source when invoked through
# __main__, but does not populate standard out streaming when the code
# is imported by other tooling.
LOG_LEVEL = logging.DEBUG
ROOT_LOGGER = logging.getLogger()
ROOT_LOGGER.setLevel(LOG_LEVEL)

# Add basic stream handler to all calls made
_stream_handler = logging.StreamHandler(sys.stdout)
_stream_handler.setLevel(LOG_LEVEL)
ROOT_LOGGER.addHandler(_stream_handler)

# Configure a separate location to store runtime information outside of systemd/rsyslog/journald services, which can
# be zero'd removed under certain build/boot instances. Preservation of this log information in a separate location
# will provide a backup mechanism to verify overall history of what was accomplished by the service on non-ephemerally
# provisioned root filesystems.
LOG_FILE_PATH = '/var/log/cfs_state_reporter.log'
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
_rfh = RotatingFileHandler(LOG_FILE_PATH, maxBytes=1024*16)
_rfh.setLevel(LOG_LEVEL)
ROOT_LOGGER.addHandler(_rfh)

# Create a representative entrypoint logger for cfs-state-reporter
LOGGER = logging.getLogger("cfs.status_reporter")

def patch_as_unconfigured_until_success(component):
    """
    Loop until CFS component information has been registered;
    tells CFS that the component (_this_ node) requires configuration.
    """
    backoff_ceiling = 30
    backoff_scalar = 2
    attempt = 0
    while True:
        # Each iteration, wait a bit longer before patching CFS component
        # state until the ceiling is reached.
        time_to_wait = backoff_scalar * attempt
        time_to_wait = min([backoff_ceiling, time_to_wait])
        sleep(time_to_wait)
        attempt += 1
        LOGGER.info("Attempt %s of contacting CFS..." %(attempt))
        session = requests_retry_session()
        try:
            mark_unconfigured(component, session)
        except UnknownComponent:
            LOGGER.warning("CFS has no record of component '%s'; nothing to report." % (component))
            LOGGER.warning("Will re-attempt patch operation as necessary.")
            continue
        except CFSComponentException as cce:
            LOGGER.warning("Unable to contact CFS to report component status: %s" % (cce))
            continue
        LOGGER.info("Zero'd configuration record for CFS component '%s'." %(component))
        return


def main():
    cfsssh_setup_main()
    component = read_identity()
    LOGGER.info("Attempting to set configuration status for '%s'" % (component))
    patch_as_unconfigured_until_success(component)


if __name__ == '__main__':
    main()
