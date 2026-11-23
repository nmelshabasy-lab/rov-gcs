"""Thread-safe publish/subscribe event bus.

Modules talk through topics (strings like "input.state"), never by importing
each other's internals.
"""
import logging
import queue
import threading
from collections import defaultdict

log = logging.getLogger(__name__)


class EventBus:
    def __init__(self):
        self._lock = threading.Lock()
        self._handlers = defaultdict(list)
        self._queues = defaultdict(list)

    def subscribe(self, topic, handler):
        """Call handler(data) whenever topic is published (runs in the publisher's thread,
        so keep handlers fast)."""
        with self._lock:
            self._handlers[topic].append(handler)

    def subscribe_queue(self, topic, maxsize=100):
        """Get a queue.Queue that receives every message on topic. Safest way to hand
        data to another thread."""
        q = queue.Queue(maxsize=maxsize)
        with self._lock:
            self._queues[topic].append(q)
        return q

    def publish(self, topic, data=None):
        with self._lock:  # copy under lock, call outside it
            handlers = list(self._handlers[topic])
            queues = list(self._queues[topic])
        for q in queues:
            try:
                q.put_nowait(data)
            except queue.Full:
                try:
                    q.get_nowait()  # drop oldest so consumers see fresh data
                    q.put_nowait(data)
                except (queue.Empty, queue.Full):
                    pass
        for handler in handlers:
            try:
                handler(data)
            except Exception:
                log.exception("Handler failed for topic %s", topic)
