"""Diagnostics support for Pandora Business."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict:
    """Return diagnostics for a config entry.
    
    This function provides diagnostic information about the Pandora Business integration,
    including configuration data and device information.
    """
    remote = hass.data[DOMAIN][config_entry.entry_id]["pandorabusinessremote"]
    
    return {
        "config_entry_data": dict(config_entry.data),
        "config_entry_options": dict(config_entry.options),
    }
