import time
from threading import Lock
from typing import Any, Optional


class TTLCache:
    """A small thread-safe in-memory cache with per-item expiry times."""

    def __init__(self):
        self._data = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        current_time = time.time()

        with self._lock:
            item = self._data.get(key)

            if item is None:
                return None

            if current_time >= item["expires_at"]:
                del self._data[key]
                return None

            return item["value"]

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = 60,
    ) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be greater than 0")

        expires_at = time.time() + ttl_seconds

        with self._lock:
            self._data[key] = {
                "value": value,
                "expires_at": expires_at,
            }

    def delete(self, key: str) -> None:
        with self._lock:
            self._data.pop(key, None)

    def delete_prefix(self, prefix: str) -> None:
        with self._lock:
            keys_to_delete = [
                key
                for key in list(self._data.keys())
                if key.startswith(prefix)
            ]

            for key in keys_to_delete:
                self._data.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()

    def size(self) -> int:
        with self._lock:
            return len(self._data)


cache = TTLCache()
