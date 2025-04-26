"""Client for Pandora for Business integration."""
import logging
import requests
from typing import Any, Dict, List, Optional, Callable

_LOGGER = logging.getLogger(__name__)

class PandoraClient:
    """Client for Pandora for Business."""

    def __init__(self, host: str, username: str, password: str) -> None:
        """Initialize the client."""
        self._host = host.rstrip("/")
        self._username = username
        self._password = password
        self._session = requests.Session()
        self._session.verify = False  # Disable SSL verification for self-signed certs
        self._logged_in = False
        self._zone_id = 1  # Default zone ID
        self._session_id = None
        self._remember_me = None
        self._on_session_update: Optional[Callable[[], None]] = None

    def set_session_update_callback(self, callback: Callable[[], None]) -> None:
        """Set callback to be called when session data changes."""
        self._on_session_update = callback

    def _get_headers(self) -> Dict[str, str]:
        """Get common headers for API requests."""
        return {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": self._host,
            "Referer": f"{self._host}/zone.shtml"
        }

    def _get_cookies(self) -> Dict[str, str]:
        """Get cookies for API requests."""
        cookies = {}
        if self._session_id:
            cookies["sessionId"] = self._session_id
        if self._remember_me:
            cookies["rememberMe"] = self._remember_me
        return cookies

    def _check_session(self) -> bool:
        """Check if the current session is still valid."""
        if not self._session_id:
            return False

        try:
            # Try to get playback info - if it fails, session is invalid
            self.get_playback_info()
            return True
        except Exception:
            return False

    def _update_session(self, session_id: str, remember_me: str) -> None:
        """Update session data and notify callback if set."""
        if session_id != self._session_id or remember_me != self._remember_me:
            self._session_id = session_id
            self._remember_me = remember_me
            if self._on_session_update:
                self._on_session_update()

    def login(self) -> None:
        """Login to the Pandora for Business server."""
        login_url = f"{self._host}/login"
        response = self._session.post(
            login_url,
            data={
                "user": self._username,
                "password": self._password,
                "rememberMe": "true"
            },
            headers={
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": self._host,
                "Referer": f"{self._host}/public/login.shtml"
            },
            timeout=10,
        )
        response.raise_for_status()

        # Extract session cookies
        cookies = response.cookies
        session_id = cookies.get("sessionId")
        remember_me = cookies.get("rememberMe")

        if not session_id:
            raise Exception("Login failed: No session ID received")

        self._update_session(session_id, remember_me)
        self._logged_in = True
        _LOGGER.debug("Successfully logged in and obtained session data")

    def ensure_session(self) -> None:
        """Ensure we have a valid session, re-authenticating if necessary."""
        if not self._check_session():
            _LOGGER.info("Session expired or invalid, re-authenticating")
            self.login()

    def get_stations(self) -> List[Dict[str, Any]]:
        """Get list of available stations."""
        self.ensure_session()
        
        stations_url = f"{self._host}/cmd"
        response = self._session.post(
            stations_url,
            params={"cmd": "zone.station.audio.getAll"},
            data={
                "zoneId": self._zone_id,
                "sortBy": "CREATION_DATE",
                "sortOrder": "NONE"
            },
            headers=self._get_headers(),
            cookies=self._get_cookies(),
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        if data["status"]["code"] != "OK":
            raise Exception(f"Failed to get stations: {data['status']}")
        return data["data"]["styles"]

    def set_station(self, station_id: str) -> None:
        """Switch to a specific station."""
        self.ensure_session()
        
        set_station_url = f"{self._host}/cmd"
        response = self._session.post(
            set_station_url,
            params={"cmd": "zone.station.audio.set"},
            data={
                "zoneId": self._zone_id,
                "styleId": station_id
            },
            headers=self._get_headers(),
            cookies=self._get_cookies(),
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        if data["status"]["code"] != "OK":
            raise Exception(f"Failed to set station: {data['status']}")

    def get_playback_info(self) -> Dict[str, Any]:
        """Get current playback information."""
        self.ensure_session()
        
        info_url = f"{self._host}/cmd"
        response = self._session.post(
            info_url,
            params={"cmd": "zone.getStatus"},
            data={"zoneId": self._zone_id},
            headers=self._get_headers(),
            cookies=self._get_cookies(),
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        if data["status"]["code"] != "OK":
            raise Exception(f"Failed to get playback info: {data['status']}")
        return data["data"]

    def skip_song(self) -> None:
        """Skip current song."""
        self.ensure_session()
        
        skip_url = f"{self._host}/cmd"
        response = self._session.post(
            skip_url,
            params={"cmd": "zone.track.skip"},
            data={
                "zoneId": self._zone_id,
                "step": 1
            },
            headers=self._get_headers(),
            cookies=self._get_cookies(),
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        if data["status"]["code"] != "OK":
            raise Exception(f"Failed to skip song: {data['status']}")

    def play(self) -> None:
        """Resume playback."""
        self.ensure_session()
        
        resume_url = f"{self._host}/cmd"
        response = self._session.post(
            resume_url,
            params={"cmd": "zone.track.resume"},
            data={"zoneId": self._zone_id},
            headers=self._get_headers(),
            cookies=self._get_cookies(),
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        if data["status"]["code"] != "OK":
            raise Exception(f"Failed to resume playback: {data['status']}") 

    def pause(self) -> None:
        """Pause playback."""
        self.ensure_session()
        
        pause_url = f"{self._host}/cmd"
        response = self._session.post(
            pause_url,
            params={"cmd": "zone.track.pause", "operationId": "0"},
            data={"zoneId": self._zone_id},
            headers=self._get_headers(),
            cookies=self._get_cookies(),
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        if data["status"]["code"] != "OK":
            raise Exception(f"Failed to pause playback: {data['status']}")
