"""Support for Pandora Business Player media player."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import PandoraBusinessAPI, PandoraBusinessAPIError
from .const import CONF_LOCATION, CONF_PASSWORD, CONF_USERNAME, DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Pandora Business Player media player from a config entry."""
    api = PandoraBusinessAPI(
        host=config_entry.data[CONF_LOCATION],
        username=config_entry.data[CONF_USERNAME],
        password=config_entry.data[CONF_PASSWORD],
    )
    await api.async_setup()
    async_add_entities([PandoraBusinessPlayerMediaPlayer(api, config_entry)])

class PandoraBusinessPlayerMediaPlayer(MediaPlayerEntity):
    """Representation of a Pandora Business Player media player."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )

    def __init__(self, api: PandoraBusinessAPI, config_entry: ConfigEntry) -> None:
        """Initialize the Pandora Business Player media player."""
        self._api = api
        self._config_entry = config_entry
        self._attr_unique_id = config_entry.entry_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Pandora Business Player",
            "manufacturer": "Pandora",
        }
        self._attr_state = MediaPlayerState.OFF
        self._attr_volume_level = 0.5
        self._attr_is_volume_muted = False
        self._attr_source_list = []
        self._attr_source = None
        self._current_track = None

    async def async_update(self) -> None:
        """Update the state of the media player."""
        try:
            info = await self._api.get_playback_info()
            self._attr_state = (
                MediaPlayerState.PLAYING if info.get("isPlaying") else MediaPlayerState.PAUSED
            )
            self._attr_volume_level = info.get("volume", 0.5) / 100.0
            self._attr_is_volume_muted = info.get("isMuted", False)
            
            # Update current track info
            if track := info.get("currentTrack"):
                self._current_track = {
                    "title": track.get("title"),
                    "artist": track.get("artist"),
                    "album": track.get("album"),
                }
            
            # Update station list
            stations = await self._api.get_stations()
            self._attr_source_list = [station["name"] for station in stations]
            if current_station := info.get("currentStation"):
                self._attr_source = current_station.get("name")
        except PandoraBusinessAPIError as err:
            _LOGGER.error("Error updating Pandora Business Player: %s", err)
            self._attr_state = MediaPlayerState.OFF

    @property
    def media_title(self) -> str | None:
        """Title of current playing media."""
        if self._current_track:
            return self._current_track["title"]
        return None

    @property
    def media_artist(self) -> str | None:
        """Artist of current playing media."""
        if self._current_track:
            return self._current_track["artist"]
        return None

    @property
    def media_album_name(self) -> str | None:
        """Album name of current playing media."""
        if self._current_track:
            return self._current_track["album"]
        return None

    async def async_media_play(self) -> None:
        """Send play command."""
        try:
            await self._api.play()
            self._attr_state = MediaPlayerState.PLAYING
        except PandoraBusinessAPIError as err:
            _LOGGER.error("Error playing Pandora Business Player: %s", err)

    async def async_media_pause(self) -> None:
        """Send pause command."""
        try:
            await self._api.pause()
            self._attr_state = MediaPlayerState.PAUSED
        except PandoraBusinessAPIError as err:
            _LOGGER.error("Error pausing Pandora Business Player: %s", err)

    async def async_media_stop(self) -> None:
        """Send stop command."""
        try:
            await self._api.pause()
            self._attr_state = MediaPlayerState.OFF
        except PandoraBusinessAPIError as err:
            _LOGGER.error("Error stopping Pandora Business Player: %s", err)

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        # TODO: Implement volume control when API supports it
        self._attr_volume_level = volume

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute (true) or unmute (false) media player."""
        # TODO: Implement mute control when API supports it
        self._attr_is_volume_muted = mute

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        try:
            stations = await self._api.get_stations()
            for station in stations:
                if station["name"] == source:
                    await self._api.set_station(station["id"])
                    self._attr_source = source
                    break
        except PandoraBusinessAPIError as err:
            _LOGGER.error("Error selecting station on Pandora Business Player: %s", err)

    async def async_media_next_track(self) -> None:
        """Send next track command."""
        try:
            await self._api.skip_song()
        except PandoraBusinessAPIError as err:
            _LOGGER.error("Error skipping track on Pandora Business Player: %s", err) 