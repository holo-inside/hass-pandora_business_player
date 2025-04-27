"""The Pandora for Business integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant import config_entries

from .const import DOMAIN, CONF_SESSION_ID, CONF_REMEMBER_ME
from .pandora_client import PandoraClient
from .config_flow import ConfigFlow

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the Pandora for Business component."""
    hass.data[DOMAIN] = {}
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Pandora for Business from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create client
    client = PandoraClient(
        host=entry.data[CONF_HOST],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
    )

    # Restore session data if it exists
    if CONF_SESSION_ID in entry.data and CONF_REMEMBER_ME in entry.data:
        client._session_id = entry.data[CONF_SESSION_ID]
        client._remember_me = entry.data[CONF_REMEMBER_ME]
        _LOGGER.debug("Restored session data from config entry")

    # Set up session update callback
    client.set_session_update_callback(lambda: _update_config_entry(hass, entry, client))

    try:
        # Verify session is still valid
        if not client._check_session():
            _LOGGER.info("Session expired or invalid, performing new login")
            client.login()
    except Exception as err:
        raise ConfigEntryNotReady(f"Failed to verify session: {err}") from err

    hass.data[DOMAIN][entry.entry_id] = client

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["media_player"])

    return True

async def _update_config_entry(hass: HomeAssistant, entry: ConfigEntry, client: PandoraClient) -> None:
    """Update the config entry with new session data."""
    new_data = {**entry.data}
    new_data[CONF_SESSION_ID] = client._session_id
    new_data[CONF_REMEMBER_ME] = client._remember_me
    
    hass.config_entries.async_update_entry(entry, data=new_data)
    _LOGGER.debug("Updated config entry with new session data")

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["media_player"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

# Register the config flow
config_entries.HANDLERS.register(DOMAIN)(ConfigFlow) 