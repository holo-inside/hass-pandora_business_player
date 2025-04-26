"""Support for Pandora for Business media player."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_ALBUM,
    ATTR_ARTIST,
    ATTR_ART_URL,
    ATTR_STATION_ID,
    ATTR_STATION_NAME,
    ATTR_TITLE,
    DOMAIN,
)
from .pandora_client import PandoraClient

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Pandora for Business media player platform."""
    client = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([PandoraBusinessMediaPlayer(client, config_entry.title)])

class PandoraBusinessMediaPlayer(MediaPlayerEntity):
    """Representation of a Pandora for Business media player."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.NEXT_TRACK
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )

    def __init__(self, client: PandoraClient, name: str) -> None:
        """Initialize the Pandora for Business media player."""
        self._client = client
        self._attr_unique_id = f"{DOMAIN}_player"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "pandora_business")},
            "name": name,
            "manufacturer": "Mood Media",
            "model": "ProFusion iO",
        }
        self._stations: list[dict[str, Any]] = []
        self._current_station: dict[str, Any] | None = None
        self._current_track: dict[str, Any] | None = None
        self._state = MediaPlayerState.OFF

    async def async_update(self) -> None:
        """Update state and attributes."""
        try:
            # Update stations list
            self._stations = await self.hass.async_add_executor_job(
                self._client.get_stations
            )

            # Update current playback info
            playback_info = await self.hass.async_add_executor_job(
                self._client.get_playback_info
            )
            
            # Update current station
            if playback_info.get("currentAudioStyle"):
                self._current_station = playback_info["currentAudioStyle"]

            # Update current track
            if playback_info.get("currentAudioSong"):
                self._current_track = playback_info["currentAudioSong"]
            
            # Update state
            if playback_info.get("state") == "PLAYED":
                self._state = MediaPlayerState.PLAYING
            elif playback_info.get("state") == "PAUSED":
                self._state = MediaPlayerState.PAUSED
            else:
                self._state = MediaPlayerState.OFF

        except Exception as err:
            _LOGGER.error("Error updating Pandora for Business: %s", err)
            self._state = MediaPlayerState.OFF

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the player."""
        return self._state

    @property
    def source_list(self) -> list[str]:
        """Return the list of available stations."""
        return [station["name"] for station in self._stations]

    @property
    def source(self) -> str | None:
        """Return the current station."""
        return self._current_station["name"] if self._current_station else None

    @property
    def media_content_type(self) -> MediaType:
        """Return the media content type."""
        return MediaType.MUSIC

    @property
    def media_title(self) -> str | None:
        """Return the title of current playing media."""
        return self._current_track["title"] if self._current_track else None

    @property
    def media_artist(self) -> str | None:
        """Return the artist of current playing media."""
        return self._current_track["artist"] if self._current_track else None

    @property
    def media_album_name(self) -> str | None:
        """Return the album name of current playing media."""
        return self._current_track["album"] if self._current_track else None

    @property
    def media_image_url(self) -> str | None:
        """Return the image URL of current playing media."""
        return self._current_track["cover"] if self._current_track else None

    async def async_media_play(self) -> None:
        """Send play command."""
        await self.hass.async_add_executor_job(self._client.play)
        self._state = MediaPlayerState.PLAYING

    async def async_media_pause(self) -> None:
        """Send pause command."""
        await self.hass.async_add_executor_job(self._client.pause)
        self._state = MediaPlayerState.PAUSED

    async def async_media_next_track(self) -> None:
        """Send next track command."""
        await self.hass.async_add_executor_job(self._client.skip_song)

    async def async_select_source(self, source: str) -> None:
        """Select a station to play."""
        station = next((s for s in self._stations if s["name"] == source), None)
        if station:
            await self.hass.async_add_executor_job(
                self._client.set_station, station["id"]
            )
            self._current_station = station 