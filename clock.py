# clock.py
import utime


class Clock:

    def __init__(self, hour, minute, second):

        self.hour   = hour % 24
        self.minute = minute % 60
        self.second = second % 60
        self._last_tick = utime.ticks_ms()
        self.setup_mode = True   # skipped when using NTP
        self.edit_field = 1      # 1 = hours, 2 = minutes
        self.running    = False
        self.paused     = False

    # Setup / edit 

    def setup_increment(self):
        if self.edit_field == 1:
            self.hour = (self.hour + 1) % 24
        else:
            self.minute = (self.minute + 1) % 60

    def setup_decrement(self):
        if self.edit_field == 1:
            self.hour = (self.hour - 1) % 24
        else:
            self.minute = (self.minute - 1) % 60

    def setup_next_field(self):
        """
        Advance through setup fields.
        Returns True when setup is complete.
        """
        if self.edit_field == 1:
            self.edit_field = 2
            return False
        else:
            self.setup_mode = False
            return True

    # Start / pause / resume 
    def start(self):
        self.second     = 0
        self.running    = True
        self.paused     = False
        self._last_tick = utime.ticks_ms()

    def pause(self):
        self.paused     = True
        self.running    = False
        self.edit_field = 1

    def resume(self):
        self.second     = 0
        self.paused     = False
        self.running    = True
        self._last_tick = utime.ticks_ms()
    # Tick 
    def tick(self):
        if not self.running:
            return
        now  = utime.ticks_ms()
        diff = utime.ticks_diff(now, self._last_tick)

        if diff >= 1000:
            self._last_tick = utime.ticks_add(
                self._last_tick,
                1000
            )
            self.second += 1
            if self.second >= 60:
                self.second  = 0
                self.minute += 1

            if self.minute >= 60:
                self.minute = 0
                self.hour  += 1

            if self.hour >= 24:
                self.hour = 0

    # Helpers
    def time_str(self):
        return "{:02d}:{:02d}:{:02d}".format(
            self.hour,
            self.minute,
            self.second
        )
    def matches(self, hour, minute):
        return (
            self.hour   == hour   and
            self.minute == minute and
            self.second == 0
        )
    def minutes_until(self, hour, minute):
        now_total    = self.hour * 60 + self.minute
        target_total = hour * 60 + minute
        diff = target_total - now_total
        if diff < -720:
            diff += 1440
        return diff

