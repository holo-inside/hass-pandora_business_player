"""Entity representing a Pandora Business Device."""
import os

from homeassistant.const import (
    ATTR_CONFIGURATION_URL,
    ATTR_HW_VERSION,
    ATTR_IDENTIFIERS,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_NAME,
    ATTR_SW_VERSION,
)

from .const import DOMAIN


class PandoraBusinessEntity:
    """Representation of a Pandora Business Device."""

    def __init__(self, hass, remote, config):
        """Initialise the PandoraBusinessEntity."""
        self._remote = remote
        self._config = config
        self._unique_id = config.unique_id

    @property
    def pandora_business_device_info(self):
        """Entity device information."""
        device_info = None
        if self._config.device_info:
            device_info = {
                ATTR_NAME: self._config.name,
                ATTR_MANUFACTURER: "Mood Media",
                ATTR_MODEL: "ProFusion iO",
            }
        return device_info
