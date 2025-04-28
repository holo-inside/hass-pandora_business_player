"""Provides device actions for Pandora Business media player."""

from typing import Final

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.device_automation import async_validate_entity_schema
from homeassistant.components.media_player import (
    ATTR_INPUT_SOURCE,
    ATTR_MEDIA_CONTENT_ID,
    ATTR_MEDIA_CONTENT_TYPE,
)
from homeassistant.components.media_player import DOMAIN as MP_DOMAIN
from homeassistant.components.media_player import (
    SERVICE_PLAY_MEDIA,
    SERVICE_SELECT_SOURCE,
    MediaPlayerEntityFeature,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_ENTITY_ID,
    CONF_TYPE,
    SERVICE_MEDIA_NEXT_TRACK,
    SERVICE_MEDIA_PAUSE,
    SERVICE_MEDIA_PLAY,
)
from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import get_supported_features
from homeassistant.helpers.typing import ConfigType, TemplateVarsType

from .const import DOMAIN

# Define all available actions for Pandora Business media player
ACTION_TYPES: Final[set[str]] = {
    "next_track",
    "play",
    "pause",
    "select_source",
    "play_media",
}

# Base schema for device actions
_ACTION_SCHEMA: Final = cv.DEVICE_ACTION_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(ACTION_TYPES),
        vol.Required(CONF_ENTITY_ID): cv.entity_id_or_uuid,
    }
)

# Schema for source selection actions
_ACTION_SCHEMA_SS: Final = _ACTION_SCHEMA.extend(
    {
        vol.Required(ATTR_INPUT_SOURCE): cv.string,
    }
)

# Schema for media playback actions
_ACTION_SCHEMA_PM: Final = _ACTION_SCHEMA.extend(
    {
        vol.Required(ATTR_MEDIA_CONTENT_ID): cv.string,
    }
)


async def async_validate_action_config(
    hass: HomeAssistant, config: ConfigType
) -> ConfigType:
    """Validate device action configuration.
    
    Args:
        hass: Home Assistant instance
        config: Configuration to validate
        
    Returns:
        Validated configuration
    """
    if config[CONF_TYPE] == "select_source":
        return async_validate_entity_schema(hass, config, _ACTION_SCHEMA_SS)
    if config[CONF_TYPE] == "play_media":
        return async_validate_entity_schema(hass, config, _ACTION_SCHEMA_PM)

    return async_validate_entity_schema(hass, config, _ACTION_SCHEMA)


async def async_get_actions(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, str]]:
    """List available device actions for Pandora Business media player.
    
    Args:
        hass: Home Assistant instance
        device_id: ID of the device to get actions for
        
    Returns:
        List of available actions
    """
    registry = er.async_get(hass)
    actions = []

    # Get all the integrations entities for this device
    for entry in er.async_entries_for_device(registry, device_id):
        if entry.platform != DOMAIN or entry.domain != MP_DOMAIN:
            continue

        supported_features = get_supported_features(hass, entry.entity_id)

        base_action: dict = {
            CONF_DEVICE_ID: device_id,
            CONF_DOMAIN: DOMAIN,
            CONF_ENTITY_ID: entry.id,
        }

        # Add actions for each entity that belongs to this integration
        if supported_features & MediaPlayerEntityFeature.PAUSE:
            actions.append({**base_action, CONF_TYPE: "pause"})
        if supported_features & MediaPlayerEntityFeature.PLAY:
            actions.append({**base_action, CONF_TYPE: "play"})
        if supported_features & MediaPlayerEntityFeature.NEXT_TRACK:
            actions.append({**base_action, CONF_TYPE: "next_track"})
        actions.extend(
            (
                {**base_action, CONF_TYPE: "select_source"},
                {**base_action, CONF_TYPE: "play_media"},
            )
        )
    return actions


async def async_call_action_from_config(
    hass: HomeAssistant,
    config: ConfigType,
    variables: TemplateVarsType,  # pylint: disable=unused-argument
    context: Context | None,
) -> None:
    """Execute a device action.
    
    Args:
        hass: Home Assistant instance
        config: Action configuration
        variables: Template variables (unused)
        context: Context for the action
    """
    service_data = {ATTR_ENTITY_ID: config[CONF_ENTITY_ID]}

    if config[CONF_TYPE] == "play":
        service = SERVICE_MEDIA_PLAY
    if config[CONF_TYPE] == "pause":
        service = SERVICE_MEDIA_PAUSE
    if config[CONF_TYPE] == "next_track":
        service = SERVICE_MEDIA_NEXT_TRACK
    if config[CONF_TYPE] == "play_media":
        service = SERVICE_PLAY_MEDIA
        service_data[ATTR_MEDIA_CONTENT_ID] = config[ATTR_MEDIA_CONTENT_ID]
        service_data[ATTR_MEDIA_CONTENT_TYPE] = DOMAIN
    if config[CONF_TYPE] == "select_source":
        service = SERVICE_SELECT_SOURCE
        service_data[ATTR_INPUT_SOURCE] = config[ATTR_INPUT_SOURCE]

    await hass.services.async_call(
        MP_DOMAIN, service, service_data, blocking=True, context=context
    )


async def async_get_action_capabilities(
    hass: HomeAssistant, config: ConfigType  # pylint: disable=unused-argument
) -> dict[str, vol.Schema]:
    """List action capabilities.
    
    Args:
        hass: Home Assistant instance
        config: Action configuration
        
    Returns:
        Dictionary of action capabilities
    """
    if config[CONF_TYPE] == "select_source":
        return {"extra_fields": vol.Schema({vol.Required(ATTR_INPUT_SOURCE): str})}
    if config[CONF_TYPE] == "play_media":
        return {"extra_fields": vol.Schema({vol.Required(ATTR_MEDIA_CONTENT_ID): str})}

    return {}
