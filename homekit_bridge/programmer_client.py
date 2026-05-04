"""Thin HTTP client for light-programmer's /mode and /kill endpoints."""
import json
import logging
import urllib.error
import urllib.request


class ProgrammerClient:
    def __init__(self, base_url: str, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, path: str, payload: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(
            url, data=data, method=method,
            headers={"Content-Type": "application/json"} if data else {},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            body = resp.read().decode()
        return json.loads(body) if body else {}

    def get_mode(self) -> dict:
        """Returns {'auto': bool, 'kill': bool}."""
        try:
            return self._request("GET", "/mode")
        except (urllib.error.URLError, json.JSONDecodeError) as e:
            logging.warning(f"get_mode failed: {e}")
            return {}

    def set_auto(self, auto: bool) -> dict:
        return self._request("POST", "/mode", {"auto": bool(auto)})

    def set_kill(self, kill: bool) -> dict:
        return self._request("POST", "/kill", {"kill": bool(kill)})
