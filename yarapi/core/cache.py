import time
import threading
from collections import OrderedDict
from typing import Union
import json
from yarapi.config import config


class LRUTTLCache:
    """
    Thread-safe in-memory LRU cache with per-key TTL.
    - Evicts expired items on access/set.
    - Enforces maxsize by LRU (least recently used).
    """

    def __init__(self, maxsize: int = 500, default_ttl: float = 3600.0):
        self._store: "OrderedDict[object, tuple[float, object]]" = OrderedDict()
        self._lock = threading.RLock()
        self._maxsize = int(maxsize)
        self._default_ttl = float(default_ttl)

    def _now(self) -> float:
        return time.monotonic()

    def serialize_key(self, data: Union[str, int, dict, list]) -> str:
        val = None

        if isinstance(data, (str, int)):
            val = str(data)

        val = json.dumps(data, sort_keys=True, default=str, separators=(",", ":"))

        return val

    def _prune_expired(self) -> None:
        t = self._now()
        expired = [k for k, (exp, _) in self._store.items() if exp <= t]
        for k in expired:
            self._store.pop(k, None)

    def _enforce_size(self) -> None:
        while len(self._store) > self._maxsize:
            # pop least-recently-used
            self._store.popitem(last=False)

    def _ttl_remaining(self, exp: float) -> float:
        return max(0.0, exp - self._now())

    def exists(self, key) -> bool:
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return False
            exp, _ = item
            if exp <= self._now():
                # expired -> drop eagerly
                self._store.pop(key, None)
                return False
            # refresh LRU position
            self._store.move_to_end(key, last=True)
            return True

    def get(self, key):
        """
        Returns value if fresh, else None.
        """
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None
            exp, val = item
            if exp <= self._now():
                self._store.pop(key, None)
                return None
            # refresh LRU
            self._store.move_to_end(key, last=True)
            return val

    def get_with_ttl(self, key):
        """
        Returns (value, ttl_remaining_seconds) if fresh, else (None, 0).
        """
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None, 0
            exp, val = item
            if exp <= self._now():
                self._store.pop(key, None)
                return None, 0
            self._store.move_to_end(key, last=True)
            return val, int(self._ttl_remaining(exp))

    def set(self, key, value, ttl: float | None = None) -> None:
        with self._lock:
            effective_ttl = float(ttl if ttl is not None else self._default_ttl)
            exp = self._now() + effective_ttl
            self._store[key] = (exp, value)
            self._store.move_to_end(key, last=True)
            # house-keeping
            self._prune_expired()
            self._enforce_size()

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


cache = LRUTTLCache(maxsize=1000, default_ttl=config.cache_ttl_seconds)
