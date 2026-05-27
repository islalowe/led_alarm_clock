# Thid file contains debounced input handling for all physical buttons and the potentiometer.
from machine import Pin
import utime
from config import DEBOUNCE_MS

class Buttons:
    def __init__(self, pin_num):
        self._pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        self._last_ms = 0

    def pressed(self):
        now = utime.ticks_ms()
        if self._pin.value() == 0:
            if utime.ticks_diff(now, self._last_ms) > DEBOUNCE_MS:
                self._last_ms = now
                return True
        return False

    def held(self):
        return self._pin.value() == 0
