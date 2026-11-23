"""Named mapping profiles stored in a human-readable JSON file."""
import json
import logging
import os
import threading

log = logging.getLogger(__name__)

EMPTY_PROFILE = {"axes": {}, "invert": {}, "buttons": {}, "keys": {}}


class ProfileManager:
    def __init__(self, path, default_name="default"):
        self.path = path
        self.default_name = default_name
        self._lock = threading.Lock()
        self._data = {"controller_profiles": {}, "profiles": {}}
        self.reload()

    def reload(self):
        """Re-read the file; safe to call while the program runs."""
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            log.error("Could not load profiles from %s: %s", self.path, exc)
            return False
        with self._lock:
            self._data = data
        log.info("Loaded %d profile(s)", len(data.get("profiles", {})))
        return True

    def save(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with self._lock, open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def names(self):
        with self._lock:
            return list(self._data.get("profiles", {}))

    def get(self, name):
        with self._lock:
            profiles = self._data.get("profiles", {})
            return profiles.get(name) or profiles.get(self.default_name) or EMPTY_PROFILE

    def set_profile(self, name, profile):
        with self._lock:
            self._data.setdefault("profiles", {})[name] = profile

    def for_controller(self, controller_name):
        """Profile linked to a recognised controller name, else the default."""
        with self._lock:
            linked = self._data.get("controller_profiles", {}).get(controller_name)
        name = linked or self.default_name
        log.info("Controller %r -> profile %r", controller_name, name)
        return name, self.get(name)
