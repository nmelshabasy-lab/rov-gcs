from gcs.bus.event_bus import EventBus


def test_handler_receives_message():
    bus, got = EventBus(), []
    bus.subscribe("t", got.append)
    bus.publish("t", 42)
    assert got == [42]


def test_queue_subscription():
    bus = EventBus()
    q = bus.subscribe_queue("t")
    bus.publish("t", "hi")
    assert q.get_nowait() == "hi"


def test_bad_handler_does_not_break_others():
    bus, got = EventBus(), []
    bus.subscribe("t", lambda d: 1 / 0)
    bus.subscribe("t", got.append)
    bus.publish("t", 1)
    assert got == [1]


def test_full_queue_drops_oldest():
    bus = EventBus()
    q = bus.subscribe_queue("t", maxsize=1)
    bus.publish("t", 1)
    bus.publish("t", 2)
    assert q.get_nowait() == 2
