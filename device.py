from threading import Thread, Event
from time import time
import commonParameter


class Device:
    def __init__(self, can_id, log):
        self._can_id = can_id
        self._log = log

    # start device
    def start(self, data):
        raise NotImplementedError("Please implement this method.")

    # stop device
    def stop(self, data):
        raise NotImplementedError("Please implement this method.")

    # check device state
    def check_state(self, data):
        raise NotImplementedError("Subclasses should implement this method to send their specific state.")
