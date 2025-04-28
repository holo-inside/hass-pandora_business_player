"""Pandora Business remote control implementation."""

import logging
from typing import Any, Dict, Optional

from .pandora_client import PandoraClient

_LOGGER = logging.getLogger(__name__)


class PandoraBusinessRemote:
    """Pandora Business remote control."""

    def __init__(self, host: str, username: str, password: str) -> None:
        """Initialize the remote."""
        self._host = host
        self._client = PandoraClient(host, username, password)
        self._device_setup = False
        self._device_type = "pandora_business"
        self._state = "idle"  # Start in idle state since we can't control power
        self._current_station = None
        self._stations = None

        # Set up session update callback
        self._client.set_session_update_callback(self._on_session_update)

    def _on_session_update(self) -> None:
        """Handle session updates."""
        self._device_setup = True
        self.update()

    @property
    def device_setup(self) -> bool:
        """Return if device is setup."""
        return self._device_setup

    @property
    def device_type(self) -> str:
        """Return the device type."""
        return self._device_type

    @property
    def state(self) -> str:
        """Return the current state."""
        return self._state

    @property
    def current_station(self) -> Optional[Dict[str, Any]]:
        """Return current station information."""
        return self._current_station

    def play(self) -> None:
        """Start playback."""
        _LOGGER.debug("Starting playback on device at %s", self._host)
        try:
            self._client.ensure_session()
            self._client.play()
            self._state = "playing"
        except Exception as ex:
            _LOGGER.error("Failed to start playback: %s", ex)
            raise

    def pause(self) -> None:
        """Pause playback."""
        _LOGGER.debug("Pausing playback on device at %s", self._host)
        try:
            self._client.ensure_session()
            self._client.pause()
            self._state = "paused"
        except Exception as ex:
            _LOGGER.error("Failed to pause playback: %s", ex)
            raise

    def stop(self) -> None:
        """Stop playback."""
        _LOGGER.debug("Stopping playback on device at %s", self._host)
        try:
            self._client.ensure_session()
            self._client.pause()  # Pandora doesn't have a stop, so we pause
            self._state = "stopped"
        except Exception as ex:
            _LOGGER.error("Failed to stop playback: %s", ex)
            raise

    def next_track(self) -> None:
        """Skip to next track."""
        _LOGGER.debug("Skipping to next track on device at %s", self._host)
        try:
            self._client.ensure_session()
            self._client.skip_song()
        except Exception as ex:
            _LOGGER.error("Failed to skip track: %s", ex)
            raise

    def update(self) -> None:
        """Update device state."""
        _LOGGER.debug("Updating device state at %s", self._host)
        try:
            self._client.ensure_session()
            status = self._client.get_playback_info()
            
            # Update current station
            if "station" in status:
                self._current_station = status["station"]
            
            # Update playback state
            if "playback" in status:
                playback_state = status["playback"].get("state", "stopped")
                if playback_state == "playing":
                    self._state = "playing"
                elif playback_state == "paused":
                    self._state = "paused"
                else:
                    self._state = "stopped"
            
            self._device_setup = True
        except Exception as ex:
            _LOGGER.error("Failed to update device state: %s", ex)
            self._device_setup = False
            raise 