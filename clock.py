import utime

class Clock:
    def __init__(self, hour, minute, second):
        self.hour   = hour % 24
        self.minute = minute % 60
        self.second = second % 60
        self._last_tick = utime.ticks_ms()

    def tick(self):
        now  = utime.ticks_ms()
        diff = utime.ticks_diff(now, self._last_tick)
        if diff >= 1000:
            self._last_tick = utime.ticks_add(self._last_tick, 1000)
            self.second += 1
            if self.second >= 60:
                self.second  = 0
                self.minute += 1
            if self.minute >= 60:
                self.minute = 0
                self.hour  += 1
            if self.hour >= 24:
                self.hour = 0

    def time_str(self):
        return "{:02d}:{:02d}:{:02d}".format(self.hour, self.minute, self.second)

    def matches(self, hour, minute):
        return self.hour == hour and self.minute == minute and self.second == 0

    def minutes_until(self, hour, minute):
        now_total    = self.hour * 60 + self.minute
        target_total = hour * 60 + minute
        diff = target_total - now_total
        if diff < -720:
            diff += 1440
        return diff
