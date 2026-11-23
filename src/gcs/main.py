"""Entry point: python -m gcs.main"""
import logging
import queue
import time

from gcs.bus.event_bus import EventBus
from gcs.config.loader import load_config
from gcs.input.profiles import ProfileManager
from gcs.input.sampler import InputSampler
from gcs.logging_setup import setup_logging


def main():
    cfg = load_config("config/config.json")
    setup_logging(**{k: v for k, v in cfg["logging"].items()})
    log = logging.getLogger("gcs.main")

    bus = EventBus()
    profiles = ProfileManager(cfg["profiles_file"], cfg["input"]["default_profile"])

    # Operator notifications (R4). A GUI will subscribe to these later.
    bus.subscribe("input.controller.connected", lambda d: print(f"[+] Controller: {d['name']}"))
    bus.subscribe("input.controller.disconnected", lambda d: print(f"[-] Lost: {d['name']}"))

    # Hotkeys: F5 reload profiles file, F6 save profiles, F7 switch to next profile (R8)
    names = profiles.names()
    current = {"i": 0}

    def on_key(d):
        if not d["down"]:
            return
        if d["key"] == "f5":
            bus.publish("config.reload_profiles")
        elif d["key"] == "f6":
            profiles.save()
            log.info("Profiles saved to %s", profiles.path)
        elif d["key"] == "f7" and names:
            current["i"] = (current["i"] + 1) % len(names)
            bus.publish("profile.select", names[current["i"]])

    bus.subscribe("input.key", on_key)

    state_q = bus.subscribe_queue("input.state", maxsize=1)  # thread-safe hand-off (R15)

    sampler = InputSampler(bus, cfg["input"], profiles)
    sampler.start()
    log.info("GCS running. Ctrl+C to quit.")
    try:
        while sampler.is_alive():
            time.sleep(1.0)  # print once a second, not at 50 Hz
            try:
                latest = state_q.get_nowait()
            except queue.Empty:
                continue
            print(latest["axes"], latest["buttons"], latest["keys"])
    except KeyboardInterrupt:
        pass
    finally:
        sampler.stop()
        sampler.join(timeout=2)


if __name__ == "__main__":
    main()
