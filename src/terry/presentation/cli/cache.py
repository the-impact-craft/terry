from sqlite3 import OperationalError
from typing import Any

from diskcache import Cache

MAX_CACHE_FIELD_SIZE = 10


class TerryCache:
    def __init__(self, cache: Cache):
        self.cache = cache

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.cache.get(key) or default
        except OperationalError:
            return default

    def set(self, key: str, value: Any):
        try:
            self.cache.set(key, value)
        except OperationalError:
            pass

    def extend(self, key, value):
        values = self.get(key) or []
        if isinstance(values, str):
            values = [values]

        values = [i for i in values if i != value]  # Remove duplicate command to move it to the top

        values.append(value)  # Add latest command at the end

        if len(values) > MAX_CACHE_FIELD_SIZE:
            values.pop(0)  # Remove oldest command if over limit

        self.set(key, values)
