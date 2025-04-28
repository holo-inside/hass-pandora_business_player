"""Constants for Pandora Business."""

from datetime import timedelta

from homeassistant.components.media_player import MediaPlayerEntityFeature
import voluptuous as vol

from homeassistant.const import Platform

DOMAIN = "pandora_business"
PANDORAREMOTE = "pandorabusinessremote"
UNDO_UPDATE_LISTENER = "undo_update_listener"
SCAN_INTERVAL = timedelta(seconds=10)

# Configuration
CONF_ADVANCED_OPTIONS = "advanced_options"

FEATURE_BASE = (
    MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.STOP
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.SELECT_SOURCE
)

TIMEOUT = 2
ERROR_TIMEOUT = 10

# Device Types
DEVICE_PANDORA_BUSINESS = "pandora_business"
