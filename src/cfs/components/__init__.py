from cfs import CFSException
from cfs import ENDPOINT as CFS_ENDPOINT

ENDPOINT = "%s/%s" % (CFS_ENDPOINT, __name__.split('.')[-1])

class CFSComponentException(CFSException):
    """
    A custom base class for all exceptions specific to
    interacting with CFS Component endpoints.
    """
