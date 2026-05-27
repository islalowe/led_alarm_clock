import utime

class CountdownTimer:
    def __init__(self):
        self.set_minutes  = 0
        self.set_seconds  = 0
        self.remaining_ms = 0
        self.running  = False
        self.finished = False
        self._last_tick = 0

    def set_time(self, minutes, seconds):
        self.set_minutes  = minutes % 60
        self.set_seconds  = seconds % 60
        self.remaining_ms = (self.set_minutes * 60 + self.set_seconds) * 1000
        self.running  = False
        self.finished = False

    def start(self):
        if self.remaining_ms > 0:
            self.running    = True
            self.finished   = False
            self._last_tick = utime.ticks_ms()

    def stop(self):
        self.running = False

    def reset(self):
        self.remaining_ms = (self.set_minutes * 60 + self.set_seconds) * 1000
        self.running  = False
        self.finished = False

    def tick(self):
        if not self.running:
            return False
        now  = utime.ticks_ms()
        diff = utime.ticks_diff(now, self._last_tick)
        if diff >= 100:
            self._last_tick    = utime.ticks_add(self._last_tick, 100)
            self.remaining_ms -= 100
            if self.remaining_ms <= 0:
                self.remaining_ms = 0
                self.running  = False
                self.finished = True
                return True
        return False

    def display_str(self):
        total_s = self.remaining_ms // 1000
        return "{:02d}:{:02d}".format(total_s // 60, total_s % 60)

    def set_str(self):
        return "{:02d}:{:02d}".format(self.set_minutes, self.set_seconds)
