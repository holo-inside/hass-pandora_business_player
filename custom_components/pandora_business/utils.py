"""Utilities for the Pandora Business platform."""

import collections
import ipaddress
import json
import logging
import re
from operator import attrgetter

_LOGGER = logging.getLogger(__name__)

def host_valid(host):
    """Return True if hostname or IP address is valid."""
    try:
        return ipaddress.ip_address(host).version == (4 or 6)
    except ValueError:
        disallowed = re.compile(r"[^a-zA-Z\d\-]")
        return all(x and not disallowed.search(x) for x in host.split("."))

def none_aware_attrgetter(attr):
    """Handle sorting with None value."""
    getter = attrgetter(attr)

    def key_func(item):
        value = getter(item)
        return (value is not None, value)

    return key_func
