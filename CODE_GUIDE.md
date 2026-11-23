# Code guide (read this so you can explain it)
Flow: main.py builds the EventBus, config, and ProfileManager, then starts the
InputSampler thread. The sampler reads pygame at 50 Hz and PUBLISHES messages on
the bus. main.py SUBSCRIBES to them. Nobody imports anyone else's internals.

- bus/event_bus.py      publish(topic, data) / subscribe(topic, fn) / subscribe_queue(topic).
                        A lock protects the lists; queues pass data between threads safely.
- config/loader.py      reads config.json over built-in defaults (R19).
- input/deadzone.py     values smaller than the dead-zone become 0, the rest rescaled (R5).
- input/profiles.py     JSON profiles: which axis/button/key means what; picks one by
                        controller name; reload() applies changes live (R8).
- input/sampler.py      the thread: handles controller plug/unplug events (R4), key
                        down/up (R2), axes/buttons/hat (R1), keeps a fixed 50 Hz (R3).
- logging_setup.py      console + rotating log file.
- tests/                pytest tests for deadzone, bus, config, profiles.

Topics: input.state, input.key, input.controller.connected/disconnected,
        config.reload_profiles, profile.select

Likely questions: Why a thread? (so GUI/network never block sampling.) Why a bus?
(modules stay independent.) Why queues? (safe thread-to-thread data, no shared state.)
Why a dead-zone? (stick drift.)
