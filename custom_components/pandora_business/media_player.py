"""The pandora_business platform allows you to control a Pandora Business player."""

import logging
from pathlib import Path
from typing import Any

from homeassistant.components.http import StaticPathConfig
from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.const import ATTR_ENTITY_ID, CONF_HOST, CONF_NAME
from homeassistant.exceptions import PlatformNotReady
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
)
from .pandora_client import PandoraClient
from .coordinator import PandoraBusinessDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


# async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):  # pylint: disable=unused-argument
#     """Set up the Pandora Business platform."""
#     host = config.get(CONF_HOST)
#     client = await hass.async_add_executor_job(PandoraClient, host)
#     if not client.device_setup:
#         raise PlatformNotReady(f"Device is not available: {host}")

#     unique_id = None
#     name = config.get(CONF_NAME)

#     await _async_setup_platform_entry(
#         config,
#         async_add_entities,
#         client,
#         unique_id,
#         name,
#         host,
#         hass,
#     )


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Pandora Business Media Player platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    name = config_entry.data[CONF_NAME]
    host = config_entry.data[CONF_HOST]

    async_add_entities(
        [PandoraBusinessMediaPlayer(coordinator, name, host)],
        True,
    )


async def _async_setup_platform_entry(
    config_item, async_add_entities, client, unique_id, name, host, hass
):
    player = PandoraBusinessDevice(
        hass,
        client,
        unique_id,
        name,
        host,
        config_item,
    )

    async_add_entities([player], False)


class PandoraBusinessDevice(MediaPlayerEntity):
    """Representation of a Pandora Business Player."""

    _attr_has_entity_name = True
    _attr_translation_key = "pandora_business"

    def __init__(
        self,
        hass,
        client,
        unique_id,
        name,
        host,
        device_info,
        config_item,
    ):
        """Initialise the Pandora Business Player."""
        self.hass = hass
        self._client = client
        self._unique_id = unique_id
        self._name = name
        self._host = host
        self._device_info = device_info
        self._config_item = config_item
        self._state = MediaPlayerState.OFF
        self._switches_generated = False
        self._old_state = None

    @property
    def device_info(self):
        """Entity device information."""
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": self._name,
            "manufacturer": "Mood Media",
            "model": "ProFusion iO",
        }

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        features = (
            MediaPlayerEntityFeature.PLAY
            | MediaPlayerEntityFeature.PAUSE
            | MediaPlayerEntityFeature.STOP
            | MediaPlayerEntityFeature.NEXT_TRACK
            | MediaPlayerEntityFeature.SELECT_SOURCE
            )

        return features

    @property
    def name(self):
        """Get the name of the devices."""
        return None

    @property
    def should_poll(self):
        """Device should be polled."""
        return True

    @property
    def state(self):
        """Return the state of the device."""
        if not self._client.device_setup:
            return MediaPlayerState.OFF

        if self._client.is_playing:
            return MediaPlayerState.PLAYING
        elif self._client.is_paused:
            return MediaPlayerState.PAUSED
        else:
            return MediaPlayerState.IDLE

    @property
    def source_list(self):
        """List of available input sources."""
        if not self._client.device_setup:
            return None

        return self._client.get_stations()

    @property
    def source(self):
        """Return the current input source."""
        if not self._client.device_setup:
            return None

        return self._client.current_station

    @property
    def media_image_url(self):
        """Image url of current playing media."""
        if not self._client.device_setup:
            return None

        return self._client.current_track_artwork

    @property
    def media_channel(self):
        """Channel currently playing."""
        if not self._client.device_setup:
            return None

        return self._client.current_station

    @property
    def media_content_type(self):
        """Content type of current playing media."""
        return MediaType.MUSIC

    @property
    def media_title(self):
        """Title of current playing media."""
        if not self._client.device_setup:
            return None

        return self._client.current_track_title

    @property
    def media_artist(self):
        """Artist of current playing media."""
        if not self._client.device_setup:
            return None

        return self._client.current_track_artist

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:radio"

    @property
    def device_class(self):
        """Entity class."""
        return MediaPlayerDeviceClass.SPEAKER

    @property
    def available(self):
        """Entity availability."""
        return self._client.device_setup

    @property
    def unique_id(self):
        """Entity unique id."""
        return self._unique_id

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        return {}

    async def async_update(self):
        """Get the latest data and update the state."""
        if not self._client.device_setup:
            return

        try:
            await self._client.update()
        except Exception as ex:
            _LOGGER.error("Error updating Pandora Business: %s", ex)

        if self._old_state != self._state:
            _LOGGER.debug("State changed to '%s' - %s", self._state, self.name)
            self._old_state = self._state

    async def async_media_play(self):
        """Send play command."""
        await self._client.play()

    async def async_media_pause(self):
        """Send pause command."""
        await self._client.pause()

    async def async_media_stop(self):
        """Send stop command."""
        await self._client.stop()

    async def async_media_next_track(self):
        """Send next track command."""
        await self._client.next_track()

    async def async_select_source(self, source):
        """Select input source."""
        await self._client.select_station(source)
