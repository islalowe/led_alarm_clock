from machine import Pin, PWM
import utime

class Beeper:
    def __init__(self, pin_num):
        self._pwm = PWM(Pin(pin_num))
        self._pwm.freq(1000)
        self._pwm.duty_u16(0)
        self._beep_until = 0

    def beep(self, duration_ms=5000):
        self._pwm.duty_u16(32768)
        self._beep_until = utime.ticks_add(utime.ticks_ms(), duration_ms)

    def update(self):
        if self._beep_until:
            if utime.ticks_diff(utime.ticks_ms(), self._beep_until) >= 0:
                self.stop()

    def stop(self):
        self._pwm.duty_u16(0)
        self._beep_until = 0
