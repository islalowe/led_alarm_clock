from machine import Pin, PWM
import utime
from display import DisplayManager
 
# ─────────────────────────────────────────────
# USER CONFIGURATION
# ─────────────────────────────────────────────
START_HOUR   = 0
START_MINUTE = 0
START_SECOND = 0
 
ALARM_HOUR   = 7
ALARM_MINUTE = 0
 
DEBOUNCE_MS  = 120
 
BEEPER_PIN   = 15
# ─────────────────────────────────────────────
 
MODE_ALARM = "ALARM"
MODE_TIMER = "TIMER"
 
# Alarm states
ALARM_ON  = "ON"
ALARM_OFF = "OFF"
ALARM_SET = "SET"
 
# Timer states
TIMER_RUN  = "RUN"
TIMER_STOP = "STOP"
TIMER_SET  = "SET"
 
 
# ── Button helper ────────────────────────────
 
class Button:
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
 
 
# ── Beeper helper ────────────────────────────
 
class Beeper:
    def __init__(self, pin_num):
        self._pwm = PWM(Pin(pin_num))
        self._pwm.freq(1000)
        self._pwm.duty_u16(0)
 
        self._beep_until = 0
 
    def beep(self, duration_ms=2000):
        self._pwm.duty_u16(32768)
        self._beep_until = utime.ticks_add(
            utime.ticks_ms(),
            duration_ms
        )
 
    def update(self):
        if self._beep_until:
            if utime.ticks_diff(
                utime.ticks_ms(),
                self._beep_until
            ) >= 0:
 
                self._pwm.duty_u16(0)
                self._beep_until = 0
 
    def stop(self):
        self._pwm.duty_u16(0)
        self._beep_until = 0
 
 
# ── Clock ────────────────────────────────────
 
class Clock:
    def __init__(self, hour, minute, second):
 
        self.hour   = hour % 24
        self.minute = minute % 60
        self.second = second % 60
 
        self._last_tick = utime.ticks_ms()
 
        # Setup / edit state (from Code 2)
        self.setup_mode   = True   # Start in setup mode
        self.edit_field   = 1      # 1 = hours, 2 = minutes
        self.running      = False  # Clock not running until setup done
        self.paused       = False  # Pause-to-edit flag
 
    # ── Setup phase ──────────────────────────
 
    def setup_increment(self):
        """Increment the currently selected setup/edit field."""
        if self.edit_field == 1:
            self.hour = (self.hour + 1) % 24
        else:
            self.minute = (self.minute + 1) % 60
 
    def setup_decrement(self):
        """Decrement the currently selected setup/edit field."""
        if self.edit_field == 1:
            self.hour = (self.hour - 1) % 24
        else:
            self.minute = (self.minute - 1) % 60
 
    def setup_next_field(self):
        """
        Advance through setup fields.
        Returns True when setup is fully complete
        (i.e. user confirmed minutes and is ready to start).
        """
        if self.edit_field == 1:
            self.edit_field = 2
            return False
        else:
            # Setup complete — ready to start
            self.setup_mode = False
            return True
 
    def start(self):
        """Begin running the clock."""
        self.second     = 0
        self.running    = True
        self.paused     = False
        self._last_tick = utime.ticks_ms()
 
    # ── Pause / edit while running ───────────
 
    def pause(self):
        """Pause the clock and enter edit mode."""
        self.paused     = True
        self.running    = False
        self.edit_field = 1
 
    def resume(self):
        """Resume the clock from its edited time."""
        self.second     = 0
        self.paused     = False
        self.running    = True
        self._last_tick = utime.ticks_ms()
 
    # ── Tick (called every loop) ─────────────
 
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
                self.second = 0
                self.minute += 1
 
            if self.minute >= 60:
                self.minute = 0
                self.hour += 1
 
            if self.hour >= 24:
                self.hour = 0
 
    def time_str(self):
        return "{:02d}:{:02d}:{:02d}".format(
            self.hour,
            self.minute,
            self.second
        )
 
    def matches(self, hour, minute):
        return (
            self.hour == hour and
            self.minute == minute and
            self.second == 0
        )
 
 
# ── Countdown Timer ──────────────────────────
 
class CountdownTimer:
 
    def __init__(self):
 
        self.set_minutes = 0
        self.set_seconds = 0
 
        self.remaining_ms = 0
 
        self.running = False
        self.finished = False
 
        self._last_tick = 0
 
    def set_time(self, minutes, seconds):
 
        self.set_minutes = minutes % 60
        self.set_seconds = seconds % 60
 
        self.remaining_ms = (
            (self.set_minutes * 60) +
            self.set_seconds
        ) * 1000
 
        self.running = False
        self.finished = False
 
    def start(self):
 
        if self.remaining_ms > 0:
 
            self.running = True
            self.finished = False
 
            self._last_tick = utime.ticks_ms()
 
    def stop(self):
        self.running = False
 
    def reset(self):
 
        self.remaining_ms = (
            (self.set_minutes * 60) +
            self.set_seconds
        ) * 1000
 
        self.running = False
        self.finished = False
 
    def tick(self):
 
        if not self.running:
            return False
 
        now  = utime.ticks_ms()
        diff = utime.ticks_diff(now, self._last_tick)
 
        if diff >= 100:
 
            self._last_tick = utime.ticks_add(
                self._last_tick,
                100
            )
 
            self.remaining_ms -= 100
 
            if self.remaining_ms <= 0:
 
                self.remaining_ms = 0
                self.running = False
                self.finished = True
 
                return True
 
        return False
 
    def display_str(self):
 
        total_s = self.remaining_ms // 1000
 
        minutes = total_s // 60
        seconds = total_s % 60
 
        return "{:02d}:{:02d}".format(
            minutes,
            seconds
        )
 
    def set_str(self):
 
        return "{:02d}:{:02d}".format(
            self.set_minutes,
            self.set_seconds
        )
 
 
# ── Main Program ─────────────────────────────
 
def main():
 
    display = DisplayManager()
    beeper  = Beeper(BEEPER_PIN)
 
    # Buttons
    btn_up   = Button(2)   # Green
    btn_down = Button(3)   # Red
    btn_set  = Button(4)   # Yellow
    btn_mode = Button(5)   # Black
    btn_edit = Button(6)   # Blue — dedicated clock edit
 
    # Clock
    clock = Clock(
        START_HOUR,
        START_MINUTE,
        START_SECOND
    )
 
    # Alarm
    alarm_hour  = ALARM_HOUR
    alarm_min   = ALARM_MINUTE
    alarm_state = ALARM_OFF
 
    # Timer
    timer = CountdownTimer()
    timer.set_time(1, 0)
 
    # IMPORTANT:
    # Start in SET mode so user can edit timer
    timer_state = TIMER_SET
 
    # System mode
    current_mode = MODE_ALARM
 
    # Startup screen
    display.startup_screen()
 
    # ══════════════════════════════════════════
    # CLOCK SETUP PHASE
    # Green/Red change value.
    # Yellow advances field (HH → MM → confirm).
    # Then Yellow again starts the clock.
    # ══════════════════════════════════════════
 
    display.clock_setup_screen(
        clock.hour,
        clock.minute,
        clock.edit_field
    )
 
    while clock.setup_mode:
 
        if btn_set.pressed():
            done = clock.setup_next_field()
            if done:
                display.clock_ready_screen(
                    clock.hour,
                    clock.minute
                )
                while True:
                    if btn_set.pressed():
                        clock.start()
                        break
                    utime.sleep_ms(50)
            else:
                display.clock_setup_screen(
                    clock.hour,
                    clock.minute,
                    clock.edit_field
                )
 
        if btn_up.pressed():
            clock.setup_increment()
            display.clock_setup_screen(
                clock.hour,
                clock.minute,
                clock.edit_field
            )
 
        if btn_down.pressed():
            clock.setup_decrement()
            display.clock_setup_screen(
                clock.hour,
                clock.minute,
                clock.edit_field
            )
 
        utime.sleep_ms(50)
 
    # ══════════════════════════════════════════
    # MAIN LOOP
    # ══════════════════════════════════════════
 
    while True:
 
        # ── Blue: clock edit (pause / advance field / resume) ──
 
        if btn_edit.pressed():
 
            if clock.running:
                # First Blue press → pause and enter edit mode
                clock.pause()
                display.clock_edit_screen(
                    clock.hour,
                    clock.minute,
                    clock.second,
                    clock.edit_field
                )
 
            elif clock.paused:
                # Subsequent Blue presses → advance field or resume
                done = clock.setup_next_field()
                if done:
                    clock.resume()
                else:
                    display.clock_edit_screen(
                        clock.hour,
                        clock.minute,
                        clock.second,
                        clock.edit_field
                    )
 
        # ── Black: mode switch (always, no clock interaction) ──
 
        if btn_mode.pressed():
 
            if current_mode == MODE_ALARM:
                current_mode = MODE_TIMER
            else:
                current_mode = MODE_ALARM
 
            beeper.stop()
 
            display.mode_switch_screen(
                current_mode
            )
 
        # ── Update beeper ─────────────────────
 
        beeper.update()
 
        # ── Clock tick ────────────────────────
 
        clock.tick()
 
        # ══════════════════════════════════════
        # ALARM MODE
        # ══════════════════════════════════════
 
        if current_mode == MODE_ALARM:
 
            # OFF → ON → SET → OFF
 
            if btn_set.pressed():
 
                if alarm_state == ALARM_OFF:
                    alarm_state = ALARM_ON
 
                elif alarm_state == ALARM_ON:
                    alarm_state = ALARM_SET
 
                else:
                    alarm_state = ALARM_OFF
 
            # Edit alarm only in SET mode
            # Green = alarm hour, Red = alarm minute
            # Only fires when clock is NOT paused
 
            if alarm_state == ALARM_SET and not clock.paused:
 
                if btn_up.pressed():
                    alarm_hour = (
                        alarm_hour + 1
                    ) % 24
 
                if btn_down.pressed():
                    alarm_min = (
                        alarm_min + 1
                    ) % 60
 
            # Trigger alarm
 
            if (
                alarm_state == ALARM_ON and
                clock.matches(alarm_hour, alarm_min)
            ):
 
                beeper.beep(5000)
 
                alarm_state = ALARM_OFF
 
            display.update_alarm(
                clock.time_str(),
                alarm_hour,
                alarm_min,
                alarm_state == ALARM_ON,
                alarm_state
            )
 
        # ══════════════════════════════════════
        # TIMER MODE
        # ══════════════════════════════════════
 
        else:
 
            # SET → RUN → STOP → SET
 
            if btn_set.pressed():
 
                # SET → RUN
                if timer_state == TIMER_SET:
 
                    timer.reset()
                    timer.start()
 
                    timer_state = TIMER_RUN
 
                # RUN → STOP
                elif timer_state == TIMER_RUN:
 
                    timer.stop()
 
                    timer_state = TIMER_STOP
 
                # STOP → SET
                else:
 
                    timer.stop()
 
                    timer_state = TIMER_SET
 
            # Timer editing
            # Only fires when clock is NOT paused
 
            if timer_state == TIMER_SET and not clock.paused:
 
                if btn_up.pressed():
 
                    timer.set_minutes = (
                        timer.set_minutes + 1
                    ) % 60
 
                if btn_down.pressed():
 
                    timer.set_seconds = (
                        timer.set_seconds + 10
                    ) % 60
 
                # IMPORTANT:
                # Update remaining time while editing
 
                timer.remaining_ms = (
                    (
                        timer.set_minutes * 60 +
                        timer.set_seconds
                    ) * 1000
                )
 
            # Timer running
 
            if timer.tick():
 
                beeper.beep(5000)
 
                timer_state = TIMER_STOP
 
            # Display
 
            if timer_state == TIMER_RUN:
                t_display = timer.display_str()
            else:
                t_display = timer.set_str()
 
            display.update_timer(
                clock.time_str(),
                t_display,
                timer_state
            )
 
        # ── Clock edit: Green/Red adjust active field ──
 
        if clock.paused:
 
            if btn_up.pressed():
                clock.setup_increment()
                display.clock_edit_screen(
                    clock.hour,
                    clock.minute,
                    clock.second,
                    clock.edit_field
                )
 
            if btn_down.pressed():
                clock.setup_decrement()
                display.clock_edit_screen(
                    clock.hour,
                    clock.minute,
                    clock.second,
                    clock.edit_field
                )
 
        utime.sleep_ms(100)
 
 
if __name__ == "__main__":
    main()
 
