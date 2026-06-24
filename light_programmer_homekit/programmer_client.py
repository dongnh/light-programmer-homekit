"""Thin HTTP client for light-programmer's /lights endpoint."""
from __future__ import annotations

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

    def get_lights(self):
        """Per-light status list ``[{id, name, connected}, …]`` from /lights.

        Returns ``None`` when light-programmer is unreachable, so the caller can
        flip the system sensor to "disconnected" and freeze the per-light ones
        rather than reporting stale state.
        """
        try:
            data = self._request("GET", "/lights")
        except (urllib.error.URLError, json.JSONDecodeError, OSError, TimeoutError) as e:
            logging.warning(f"get_lights failed: {e}")
            return None
        if not isinstance(data, dict):
            return None
        return data.get("lights", [])
