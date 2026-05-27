from machine import Pin, PWM, SPI, ADC
import utime
from displayv2 import DisplayManager
import max7219
import timekeeping

# USER CONFIGURATION

START_HOUR   = 6
START_MINUTE = 59
START_SECOND = 0

ALARM_HOUR   = 7
ALARM_MINUTE = 0

DEBOUNCE_MS = 120

BEEPER_PIN = 15

WIFI_SSID     = "Your iPhone"
WIFI_PASSWORD = "yourpassword"

# LED MATRIX

MATRIX_SPI_ID = 0
MATRIX_SCK    = 18
MATRIX_MOSI   = 19
MATRIX_CS     = 17
MATRIX_NUM    = 4

# SUNRISE SETTINGS

SUNRISE_LEAD_MINUTES = 10
SUNRISE_START_PCT    = 2

# LDR SETTINGS

LDR_PIN       = 26
LDR_THRESHOLD = 30000  # above this = bright room

# FLASH SETTINGS

FLASH_STOP_PIN     = 6
FLASH_TIMEOUT_MINS = 10

# ─────────────────────────────────────────────

MODE_ALARM = "ALARM"
MODE_TIMER = "TIMER"

ALARM_ON  = "ON"
ALARM_OFF = "OFF"
ALARM_SET = "SET"

TIMER_RUN  = "RUN"
TIMER_STOP = "STOP"
TIMER_SET  = "SET"


# ─────────────────────────────────────────────
# LDR
# ─────────────────────────────────────────────

ldr = ADC(Pin(LDR_PIN))

def get_sunrise_start_pct():
    # Low-light = 10%, bright room = 20%
    reading = ldr.read_u16()
    print("LDR reading:", reading)
    if reading >= LDR_THRESHOLD:
        return 20
    return 10


# ─────────────────────────────────────────────
# BUTTON
# ─────────────────────────────────────────────

class Button:

    def __init__(self, pin_num):

        self._pin = Pin(
            pin_num,
            Pin.IN,
            Pin.PULL_UP
        )

        self._last_ms = 0

    def pressed(self):

        now = utime.ticks_ms()

        if self._pin.value() == 0:

            if utime.ticks_diff(
                now,
                self._last_ms
            ) > DEBOUNCE_MS:

                self._last_ms = now
                return True

        return False

    def held(self):

        return self._pin.value() == 0


# ─────────────────────────────────────────────
# BEEPER
# ─────────────────────────────────────────────

class Beeper:

    def __init__(self, pin_num):

        self._pwm = PWM(Pin(pin_num))

        self._pwm.freq(1000)
        self._pwm.duty_u16(0)

        self._beep_until = 0

    def beep(self, duration_ms=5000):

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

                self.stop()

    def stop(self):

        self._pwm.duty_u16(0)
        self._beep_until = 0


# ─────────────────────────────────────────────
# LED MATRIX
# ─────────────────────────────────────────────

class LEDMatrix:

    def __init__(
        self,
        spi_id,
        sck_pin,
        mosi_pin,
        cs_pin,
        num_chips
    ):

        spi = SPI(
            spi_id,
            sck=Pin(sck_pin),
            mosi=Pin(mosi_pin)
        )

        cs = Pin(cs_pin, Pin.OUT)

        self._m = max7219.Matrix8x8(
            spi,
            cs,
            num_chips
        )

        self._m.brightness(0)
        self._m.fill(0)
        self._m.show()

        # Sunrise state
        self._sunrise_active    = False
        self._sunrise_start_ms  = 0
        self._sunrise_dur_ms    = 0
        self._sunrise_start_pct = SUNRISE_START_PCT
        self._ramp_dur_ms       = 0  # ADD THIS

        # Flash state
        self._flash_active   = False
        self._flash_on       = False
        self._flash_next_ms  = 0
        self._flash_start_ms = 0

    # ── BRIGHTNESS ───────────────────────────

    def _set_brightness_pct(self, pct):

        level = max(
            0,
            min(15, int((pct / 100.0) * 15))
        )

        self._m.brightness(level)

    # ── SUNRISE ──────────────────────────────

    def start_sunrise(self, duration_minutes):

        self._sunrise_dur_ms = (
            duration_minutes * 60 * 1000
        )

        self._sunrise_start_ms = utime.ticks_ms()

        self._sunrise_active = True

        # Read LDR to set starting brightness
        self._sunrise_start_pct = get_sunrise_start_pct()
        if self._sunrise_start_pct >= 20:
            self._ramp_dur_ms = self._sunrise_dur_ms // 2
        else:
            self._ramp_dur_ms = self._sunrise_dur_ms

        print("Sunrise start brightness:", self._sunrise_start_pct, "%")

        self._m.fill(1)

        self._set_brightness_pct(
            self._sunrise_start_pct
        )

        self._m.show()

    def stop_sunrise(self):

        self._sunrise_active = False

        self._m.fill(0)

        self._set_brightness_pct(0)

        self._m.show()

    def sunrise_active(self):

        return self._sunrise_active

    # ── FLASH ────────────────────────────────

    def start_flash(self):

        self._flash_active = True
        self._flash_on = True

        self._flash_start_ms = utime.ticks_ms()
        self._flash_next_ms  = utime.ticks_ms()

        self._m.fill(1)

        self._set_brightness_pct(100)

        self._m.show()

    def stop_flash(self):

        self._flash_active = False
        self._flash_on = False

        self._m.fill(0)
        self._m.show()

    def flash_active(self):

        return self._flash_active

    # ── UPDATE ───────────────────────────────

    def update(self):

        now = utime.ticks_ms()

        # ── SUNRISE UPDATE ───────────────────

        if self._sunrise_active:

            elapsed = utime.ticks_diff(
                now,
                self._sunrise_start_ms
            )

            progress = elapsed / self._ramp_dur_ms

            if progress >= 1.0:

                self._set_brightness_pct(100)

                self._m.fill(1)

                self._m.show()

            else:

                brightness = (
                    self._sunrise_start_pct +
                    (
                        (100 - self._sunrise_start_pct)
                        * progress
                    )
                )

                self._set_brightness_pct(
                    brightness
                )

        # ── FLASH UPDATE ─────────────────────

        if self._flash_active:

            elapsed_mins = (
                utime.ticks_diff(
                    now,
                    self._flash_start_ms
                ) // 60000
            )

            if elapsed_mins >= FLASH_TIMEOUT_MINS:

                self.stop_flash()
                return

            if elapsed_mins < 2:

                half_period = 500

            elif elapsed_mins < 4:

                half_period = 250

            else:

                half_period = 125

            if utime.ticks_diff(
                now,
                self._flash_next_ms
            ) >= 0:

                self._flash_on = not self._flash_on

                self._m.fill(
                    1 if self._flash_on else 0
                )

                self._m.show()

                self._flash_next_ms = utime.ticks_add(
                    now,
                    half_period
                )


# ─────────────────────────────────────────────
# CLOCK
# ─────────────────────────────────────────────
class Clock:

    def __init__(self, hour, minute, second):
        self.hour   = hour % 24
        self.minute = minute % 60
        self.second = second % 60
        self._last_tick = utime.ticks_ms()
        self.setup_mode = True
        self.edit_field = 1
        self.running    = False
        self.paused     = False

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
        if self.edit_field == 1:
            self.edit_field = 2
            return False
        else:
            self.setup_mode = False
            return True

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

    def tick(self):
        if not self.running:
            return
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


# ─────────────────────────────────────────────
# TIMER
# ─────────────────────────────────────────────

class CountdownTimer:

    def __init__(self):

        self.set_minutes  = 0
        self.set_seconds  = 0

        self.remaining_ms = 0

        self.running  = False
        self.finished = False

        self._last_tick = 0

    def set_time(self, minutes, seconds):

        self.set_minutes = minutes % 60
        self.set_seconds = seconds % 60

        self.remaining_ms = (
            (
                self.set_minutes * 60 +
                self.set_seconds
            ) * 1000
        )

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
            (
                self.set_minutes * 60 +
                self.set_seconds
            ) * 1000
        )

        self.running = False
        self.finished = False

    def tick(self):

        if not self.running:
            return False

        now = utime.ticks_ms()

        diff = utime.ticks_diff(
            now,
            self._last_tick
        )

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

        return "{:02d}:{:02d}".format(
            total_s // 60,
            total_s % 60
        )

    def set_str(self):

        return "{:02d}:{:02d}".format(
            self.set_minutes,
            self.set_seconds
        )


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():

    display = DisplayManager()

    beeper = Beeper(BEEPER_PIN)

    matrix = LEDMatrix(
        MATRIX_SPI_ID,
        MATRIX_SCK,
        MATRIX_MOSI,
        MATRIX_CS,
        MATRIX_NUM
    )

    # Buttons
    btn_up        = Button(2)
    btn_down      = Button(3)
    btn_set       = Button(4)
    btn_mode      = Button(5)
    btn_flashstop = Button(FLASH_STOP_PIN)
    btn_edit      = Button(7)   # Blue — dedicated clock edit

    # # Clock
    # clock = Clock(
    #     START_HOUR,
    #     START_MINUTE,
    #     START_SECOND
    # )
    # CLOCK:
  

    if timekeeping.connect_wifi(WIFI_SSID, WIFI_PASSWORD):
        try:
            timekeeping.sync_time_ntp()
        except OSError:
            pass  # fall through to RTC default (00:00:00)
    h, m = timekeeping.get_time()
    clock = Clock(h, m, 0)
    clock.setup_mode = False
    clock.running    = True
    clock._last_tick = utime.ticks_ms()

    # Alarm
    alarm_hour  = ALARM_HOUR
    alarm_min   = ALARM_MINUTE
    alarm_state = ALARM_OFF

    sunrise_triggered  = False
    sunrise_manual_off = False
    alarm_cancelled    = False

    # Timer
    timer = CountdownTimer()

    timer.set_time(0, 0)

    timer_state = TIMER_SET

    # Mode
    current_mode = MODE_ALARM

    display.startup_screen()

    while True:

        if btn_edit.pressed():
            if clock.running:
                clock.pause()
                display.clock_edit_screen(clock.hour, clock.minute, clock.second, clock.edit_field)
            elif clock.paused:
                done = clock.setup_next_field()
                if done:
                    clock.resume()
                else:
                    display.clock_edit_screen(clock.hour, clock.minute, clock.second, clock.edit_field)
        # ── MODE SWITCH ─────────────────────

        if btn_mode.pressed():

            current_mode = (
                MODE_TIMER
                if current_mode == MODE_ALARM
                else MODE_ALARM
            )

            beeper.stop()

            display.mode_switch_screen(
                current_mode
            )

        # ── UPDATE SYSTEMS ──────────────────

        beeper.update()

        matrix.update()

        clock.tick()

        # ── MIDNIGHT RESET ──────────────────

        if (
            clock.hour == 0 and
            clock.minute == 0 and
            clock.second == 0
        ):

            sunrise_triggered  = False
            sunrise_manual_off = False
            alarm_cancelled    = False

        # ── GP6 STOP BUTTON ─────────────────

        if btn_flashstop.pressed():

            matrix.stop_flash()

            matrix.stop_sunrise()

            beeper.stop()

            sunrise_manual_off = True
            alarm_cancelled    = True

        # ════════════════════════════════════
        # ALARM MODE
        # ════════════════════════════════════

        if current_mode == MODE_ALARM:

            # OFF → ON → SET → OFF

            if btn_set.pressed():

                if alarm_state == ALARM_OFF:

                    alarm_state = ALARM_ON

                    sunrise_triggered  = False
                    sunrise_manual_off = False
                    alarm_cancelled    = False

                elif alarm_state == ALARM_ON:

                    alarm_state = ALARM_SET

                else:

                    alarm_state = ALARM_OFF

                    matrix.stop_flash()
                    matrix.stop_sunrise()

            # ── SET ALARM TIME ──────────────

            if alarm_state == ALARM_SET:

                if btn_up.pressed():

                    alarm_hour = (
                        (alarm_hour + 1) % 24
                    )

                if btn_down.pressed():

                    alarm_min = (
                        (alarm_min + 1) % 60
                    )

            # ── SUNRISE TRIGGER ─────────────

            if (
                alarm_state == ALARM_ON and
                not sunrise_triggered and
                not sunrise_manual_off and
                not alarm_cancelled
            ):

                mins_to_alarm = clock.minutes_until(
                    alarm_hour,
                    alarm_min
                )

                if (
                    0 <= mins_to_alarm <=
                    SUNRISE_LEAD_MINUTES
                ):

                    matrix.start_sunrise(
                        SUNRISE_LEAD_MINUTES
                    )

                    sunrise_triggered = True

            # ── ALARM TRIGGER ───────────────

            if (
                alarm_state == ALARM_ON and
                not alarm_cancelled and
                clock.matches(
                    alarm_hour,
                    alarm_min
                )
            ):

                if matrix.sunrise_active():

                    matrix.stop_sunrise()

                matrix.start_flash()

                beeper.beep(5000)

            # ── DISPLAY ─────────────────────

            display.update_alarm(
                clock.time_str(),
                alarm_hour,
                alarm_min,
                alarm_state == ALARM_ON,
                alarm_state
            )

        # ════════════════════════════════════
        # TIMER MODE
        # ════════════════════════════════════

        else:

            # SET → RUN → STOP → SET

            if btn_set.pressed():

                if timer_state == TIMER_SET:

                    timer.reset()
                    timer.start()

                    timer_state = TIMER_RUN

                elif timer_state == TIMER_RUN:

                    timer.stop()

                    timer_state = TIMER_STOP

                else:

                    timer.stop()

                    matrix.stop_flash()

                    beeper.stop()

                    timer_state = TIMER_SET

            # ── TIMER EDIT ──────────────────

            if timer_state == TIMER_SET:

                if btn_up.pressed():

                    timer.set_minutes = (
                        (timer.set_minutes + 1) % 60
                    )

                if btn_down.pressed():

                    timer.set_seconds = (
                        (timer.set_seconds + 10) % 60
                    )

                timer.remaining_ms = (
                    (
                        timer.set_minutes * 60 +
                        timer.set_seconds
                    ) * 1000
                )

            # ── TIMER COUNTDOWN ─────────────

            if timer.tick():

                beeper.beep(5000)

                matrix.start_flash()

                timer_state = TIMER_STOP

            # ── DISPLAY ─────────────────────

            if timer_state == TIMER_RUN:

                t_display = timer.display_str()

            else:

                t_display = timer.set_str()

            display.update_timer(
                clock.time_str(),
                t_display,
                timer_state
            )

        if clock.paused:
            if btn_up.pressed():
                clock.setup_increment()
                display.clock_edit_screen(clock.hour, clock.minute, clock.second, clock.edit_field)
            if btn_down.pressed():
                clock.setup_decrement()
                display.clock_edit_screen(clock.hour, clock.minute, clock.second, clock.edit_field)
        utime.sleep_ms(10)


# ─────────────────────────────────────────────

if __name__ == "__main__":

    main()







#TODO - THIS IS MAIN THAT JUST IMPORTS OTHER FILES
# # main.py
# from config      import *
# from button      import Button
# from beeper      import Beeper
# from led_matrix  import LEDMatrix
# from clock       import Clock
# from timer       import CountdownTimer
# from displayv2   import DisplayManager
# import timekeeping

# MODE_ALARM = "ALARM"
# MODE_TIMER = "TIMER"
# ALARM_ON   = "ON"
# ALARM_OFF  = "OFF"
# ALARM_SET  = "SET"
# TIMER_RUN  = "RUN"
# TIMER_STOP = "STOP"
# TIMER_SET  = "SET"

# def main():
#     display = DisplayManager()
#     beeper  = Beeper(BEEPER_PIN)
#     matrix  = LEDMatrix(MATRIX_SPI_ID, MATRIX_SCK, MATRIX_MOSI, MATRIX_CS, MATRIX_NUM)

#     btn_up        = Button(2)
#     btn_down      = Button(3)
#     btn_set       = Button(4)
#     btn_mode      = Button(5)
#     btn_flashstop = Button(FLASH_STOP_PIN)

#     if timekeeping.connect_wifi(WIFI_SSID, WIFI_PASSWORD):
#         try:
#             timekeeping.sync_time_ntp()
#         except OSError:
#             pass

#     h, m = timekeeping.get_time()
#     clock = Clock(h, m, 0)

#     # ... rest of the loop unchanged
