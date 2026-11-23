"""Input sampler: runs in its own thread at a fixed rate and publishes to the event bus.

Topics published:
  input.state                 -> dict snapshot every tick
  input.controller.connected  -> {"name", "profile"}
  input.controller.disconnected -> {"name"}
  input.key                   -> {"key", "down"}
"""
import logging
import queue
import threading
import time

from .deadzone import apply_deadzone

log = logging.getLogger(__name__)


class InputSampler(threading.Thread):
    def __init__(self, bus, input_cfg, profiles):
        super().__init__(name="input-sampler", daemon=True)
        self.bus = bus
        self.rate = float(input_cfg["sample_rate_hz"])
        self.deadzone = float(input_cfg["deadzone"])
        self.profiles = profiles
        self._stop_event = threading.Event()
        self._reload_event = threading.Event()
        self._select_q = queue.Queue()  # profile names requested by other modules
        self.bus.subscribe("profile.select", self._select_q.put)
        self.bus.subscribe("config.reload_profiles", lambda _d: self._reload_event.set())

    def stop(self):
        self._stop_event.set()

    def run(self):
        import pygame  # imported here so tests don't need a display

        pygame.init()
        pygame.joystick.init()
        pygame.display.set_mode((320, 100))  # keyboard events need a window with focus
        pygame.display.set_caption("ROV input (keep focused)")

        joysticks = {}  # instance_id -> Joystick
        profile = self.profiles.get(self.profiles.default_name)
        keys_down = set()
        period = 1.0 / self.rate
        next_tick = time.perf_counter()
        log.info("Input sampler started at %.0f Hz", self.rate)

        while not self._stop_event.is_set():
            if self._reload_event.is_set():
                self._reload_event.clear()
                if self.profiles.reload() and joysticks:
                    name = next(iter(joysticks.values())).get_name()
                    _, profile = self.profiles.for_controller(name)
                log.info("Profiles reloaded without restart")

            while True:
                try:
                    wanted = self._select_q.get_nowait()
                except queue.Empty:
                    break
                profile = self.profiles.get(wanted)
                log.info("Switched to profile %r", wanted)

            for event in pygame.event.get():
                if event.type == pygame.JOYDEVICEADDED:
                    try:
                        joy = pygame.joystick.Joystick(event.device_index)
                        joysticks[joy.get_instance_id()] = joy
                        pname, profile = self.profiles.for_controller(joy.get_name())
                        log.warning("Controller connected: %s", joy.get_name())
                        self.bus.publish("input.controller.connected",
                                         {"name": joy.get_name(), "profile": pname})
                    except pygame.error:
                        log.exception("Failed to open controller")
                elif event.type == pygame.JOYDEVICEREMOVED:
                    joy = joysticks.pop(event.instance_id, None)
                    name = joy.get_name() if joy else "unknown"
                    log.warning("Controller disconnected: %s", name)
                    self.bus.publish("input.controller.disconnected", {"name": name})
                elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                    key = pygame.key.name(event.key)
                    down = event.type == pygame.KEYDOWN
                    (keys_down.add if down else keys_down.discard)(key)
                    self.bus.publish("input.key", {"key": key, "down": down})
                elif event.type == pygame.QUIT:
                    self.stop()

            self.bus.publish("input.state", self._snapshot(joysticks, profile, keys_down))

            next_tick += period
            delay = next_tick - time.perf_counter()
            if delay > 0:
                time.sleep(delay)
            else:
                next_tick = time.perf_counter()  # fell behind; resync

        pygame.quit()
        log.info("Input sampler stopped")

    def _snapshot(self, joysticks, profile, keys_down):
        axes, buttons, hat, name = {}, {}, (0, 0), None
        if joysticks:
            joy = next(iter(joysticks.values()))
            name = joy.get_name()
            invert = profile.get("invert", {})
            for i in range(joy.get_numaxes()):
                value = apply_deadzone(joy.get_axis(i), self.deadzone)
                if invert.get(str(i)):
                    value = -value
                axes[profile["axes"].get(str(i), f"axis_{i}")] = round(value, 3)
            for i in range(joy.get_numbuttons()):
                buttons[profile["buttons"].get(str(i), f"button_{i}")] = bool(joy.get_button(i))
            if joy.get_numhats() > 0:
                hat = joy.get_hat(0)
        actions = sorted(profile.get("keys", {}).get(k, k) for k in keys_down)
        return {"time": time.time(), "controller": name, "axes": axes,
                "buttons": buttons, "hat": hat, "keys": actions}
