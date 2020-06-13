import logging
import sys
from time import sleep

from cfs.client import requests_retry_session
from cfs.node_identity import read_identity
from cfs.components.state import mark_unconfigured, CFSComponentException, UnknownComponent

# Configure Project Level Logging options when invoked through __main__;
# This allows the whole project to log from their source when invoked throuh
# __main__, but does not populate stdandard out streamming when the code
# is imported by other tooling.
LOG_LEVEL = logging.DEBUG
PROJECT_LOGGER = logging.getLogger('cfs')
LOGGER = logging.getLogger('cfs.status_reporter')
LOGGER.setLevel(LOG_LEVEL)
_stream_handler = logging.StreamHandler(sys.stdout)
_stream_handler.setLevel(LOG_LEVEL)
PROJECT_LOGGER.addHandler(_stream_handler)
PROJECT_LOGGER.setLevel(logging.DEBUG)



def patch_as_unconfigured_until_success(component):
    """
    Loop until CFS component information has been registered;
    tells CFS that the component (_this_ node) requires configuration.
    """
    backoff_ceiling=30
    backoff_scalar=2
    session = requests_retry_session()
    attempt = 0
    while True:
        # Each iteration, wait a bit longer before patching CFS component
        # state until the ceiling is reached.
        time_to_wait = backoff_scalar * attempt
        time_to_wait = min([backoff_ceiling, time_to_wait])
        sleep(time_to_wait)
        attempt += 1
        LOGGER.info("Attempt %s of contacting CFS..." %(attempt))
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
    component = read_identity()
    LOGGER.info("Attempting to set configuration status for '%s'" % (component))
    patch_as_unconfigured_until_success(component)


if __name__ == '__main__':
    main()