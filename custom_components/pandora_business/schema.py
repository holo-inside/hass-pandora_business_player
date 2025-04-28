"""Schema for Pandora Business Integration."""

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.media_player import PLATFORM_SCHEMA
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_USERNAME

from .const import (
    CONF_ADVANCED_OPTIONS,
    DEFAULT_ENTITY_NAME,
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_NAME): cv.string,
        vol.Optional(CONF_ADVANCED_OPTIONS, default=False): cv.boolean,
    }
)

DATA_SCHEMA = {
    vol.Required(CONF_HOST): str,
    vol.Required(CONF_NAME, default=DEFAULT_ENTITY_NAME): str,
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
}
