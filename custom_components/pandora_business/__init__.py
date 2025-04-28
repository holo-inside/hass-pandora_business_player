"""Initialise."""

import json
import logging
import os

from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_ADVANCED_OPTIONS,
    DEVICE_PANDORA_BUSINESS,
    DOMAIN,
    PANDORAREMOTE,
    UNDO_UPDATE_LISTENER,
)
from .remote import PandoraBusinessRemote
# from .schema import PLATFORM_SCHEMA

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.MEDIA_PLAYER]


async def async_setup(hass, config):  # pylint: disable=unused-argument
    """Set up the integration."""
    return True


async def async_setup_entry(hass, config_entry):
    """Set up a config entry."""
    _LOGGER.debug(
        "Load %s, %s", config_entry.data[CONF_HOST], config_entry.unique_id
    )
    host = config_entry.data[CONF_HOST]
    name = config_entry.data[CONF_NAME]
    username = config_entry.data[CONF_USERNAME]
    password = config_entry.data[CONF_PASSWORD]

    undo_listener = config_entry.add_update_listener(update_listener)

    hass.data.setdefault(DOMAIN, {})
    remote = await hass.async_add_executor_job(
        PandoraBusinessRemote, host, username, password
    )
    if not remote.device_setup:
        raise ConfigEntryNotReady(f"Device is not available: {host}")

    hass.data[DOMAIN][config_entry.entry_id] = {
        PANDORAREMOTE: remote,
        UNDO_UPDATE_LISTENER: undo_listener,
    }

    await hass.config_entries.async_forward_entry_setups(
        config_entry, PLATFORMS
    )

    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    _LOGGER.debug(
        "Unload %s, %s", config_entry.data[CONF_HOST], config_entry.unique_id
    )
    host = config_entry.data[CONF_HOST]
    remote = await hass.async_add_executor_job(PandoraBusinessRemote, host)
    process_platforms = [
        component
        for component in PLATFORMS
        if remote.device_type == DEVICE_PANDORA_BUSINESS or component == Platform.MEDIA_PLAYER
    ]

    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, process_platforms
    )

    hass.data[DOMAIN][config_entry.entry_id][UNDO_UPDATE_LISTENER]()

    if unload_ok:
        _LOGGER.debug(
            "Unload OK %s, %s",
            config_entry.data[CONF_HOST],
            config_entry.unique_id,
        )
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def update_listener(hass, config_entry):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_migrate_entry(hass, config_entry):
    # sourcery skip: assign-if-exp, boolean-if-exp-identity, merge-dict-assign
    """Migrate old entry."""
    _LOGGER.debug(
        "Migrating %s from version %s", config_entry.title, config_entry.version
    )

    # if config_entry.version == 1:
    #     new_options = {**config_entry.options}
    #     config_entry.version = 2
    #     hass.config_entries.async_update_entry(config_entry, options=new_options)

    _LOGGER.info(
        "Migration of %s to version %s successful",
        config_entry.title,
        config_entry.version,
    )

    return True
