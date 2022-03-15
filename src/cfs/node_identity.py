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
This module contains a set of operations that allow a node to
query its hardware identity. A node's given identity is bestowed
upon it via HSM, however it is not always recorded in the same
way for any given node.
"""

import os
import re
from cfs import CFSException

XNAME_PATTERN = re.compile('x\d+?c\d+s\d+b\dn\d+', re.M)


class UnknownIdentity(CFSException):
    """
    For any situation that could arise where the identity of a running
    system cannot be ascertained.
    """


def proc_cmdline():
    """
    Yields key value pairs from a node's /proc/cmdline file in
    the order they appear.

    Emits both tuples and strings.
    """
    try:
        with open('/proc/cmdline', 'r') as procfile:
            boot_options = procfile.read().strip().split(' ')
            for entry in boot_options:
                try:
                    yield entry.split('=')
                except IndexError:
                    yield entry
    except OSError as ose:
        raise UnknownIdentity(ose)


def xname_from_proc_cmdline():
    """
    Attempts to read an xname identity from /proc/cmdline and returns it.

    If the value is not found, raise an UnknownIdentity exception.
    """
    for entry in proc_cmdline():
        try:
            key, value = entry
            if key == 'xname':
                return value
        except ValueError:
            # Single string values are not interesting to us
            continue
    raise UnknownIdentity("An xname value was not discovered on '/proc/cmdline'")


def identity_from_environment():
    """
    As an override or replacement for an entry in /proc/cmdline,
    check to see if the user has provided an override in the environment.
    """
    ident_string = 'NODE_IDENTITY'
    try:
        return os.environ[ident_string]
    except KeyError:
        raise UnknownIdentity("Node identity not passed in via environment '%s'" % (ident_string))


def read_identity():
    """
    Obtain identity information from defined sources in the desired order.
    Return the first viable identity.
    If no identity is discovered, raise an UnknownIdentity exception.
    """
    for method in (identity_from_environment,
                   xname_from_proc_cmdline):
        try:
            return method()
        except UnknownIdentity as ui:
            continue
    raise UnknownIdentity("All available methods used to determine node hardware "
                          "identity have failed.")
