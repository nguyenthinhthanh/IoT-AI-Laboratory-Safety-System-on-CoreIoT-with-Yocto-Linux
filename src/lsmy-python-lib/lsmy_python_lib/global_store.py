import threading
import logging

log = logging.getLogger("global-store")

class GlobalStore:
    def __init__(self):
        self._lock = threading.Lock()
        
        self._data = {
            "wifi_status": "DISCONNECTED",
            "is_ap_mode": False,
            "is_sta_mode": True,
        }

    def set(self, key, value):
        with self._lock:
            if key in self._data:
                if self._data[key] != value:
                    log.info(f"Update {key}: {self._data[key]} -> {value}")
                    self._data[key] = value
            else:
                log.warning(f"Key '{key}' not found in GlobalStore.")

    def get(self, key, default=None):
        with self._lock:
            return self._data.get(key, default)

    def increment(self, key, amount=1):
        with self._lock:
            if isinstance(self._data.get(key), (int, float)):
                self._data[key] += amount
            else:
                log.error(f"Cannot increment non-numeric key: {key}")

# Global instance
Global_Store = GlobalStore()