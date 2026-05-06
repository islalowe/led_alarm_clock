 # This file contains timekeeping logic; tracks current time, alarm time, and handles the alarm trigger condition.


"""
LED Matrix Flashing Alarm Clock
Uses the Pico's internal RTC to trigger a flashing alarm at a configured time.

Config: set ALARM_HOUR and ALARM_MINUTE below.
Note: The Pico's internal clock resets on power loss. Set the time at boot
      using machine.RTC().datetime((year, month, day, weekday, hour, min, sec, subsec))
      or swap this file's RTC source for a DS1307/DS3231 module later.
"""

import machine
import max7219
import time

# ── Alarm time config ──────────────────────────────────────────────
ALARM_HOUR   = 9
ALARM_MINUTE = 8

# ── Flash config ───────────────────────────────────────────────────
FLASH_ON_MS  = 500   # how long LEDs stay ON  (milliseconds)
FLASH_OFF_MS = 500   # how long LEDs stay OFF (milliseconds)
FLASH_COUNT  = 20    # number of flashes before stopping (0 = forever)

# ── Display setup ──────────────────────────────────────────────────
spi = machine.SPI(0,
                  sck=machine.Pin(6),
                  mosi=machine.Pin(7))
cs      = machine.Pin(5, machine.Pin.OUT)
display = max7219.Matrix8x8(spi, cs, 4)
display.brightness(15)

# ── RTC setup ─────────────────────────────────────────────────────
rtc = machine.RTC()

# Uncomment and edit this line to set the Pico clock after a power loss:
# rtc.datetime((2025, 1, 1, 0, 7, 29, 50, 0))  # (Y, M, D, weekday, H, Min, S, subsec)


def flash_alarm():
    """Flash all LEDs on/off for FLASH_COUNT cycles (or forever if 0)."""
    count = 0
    while FLASH_COUNT == 0 or count < FLASH_COUNT:
        display.fill(1)
        display.show()
        time.sleep_ms(FLASH_ON_MS)

        display.fill(0)
        display.show()
        time.sleep_ms(FLASH_OFF_MS)

        count += 1

    # Leave display off after alarm ends
    display.fill(0)
    display.show()


def already_triggered_today(last_trigger_day, now):
    """Return True if we already fired the alarm today."""
    return last_trigger_day == now[2]  # index 2 = day-of-month


# ── Main loop ─────────────────────────────────────────────────────
last_trigger_day = -1  # tracks which calendar day the alarm last fired

print("Alarm clock running. Alarm set for {:02d}:{:02d}".format(ALARM_HOUR, ALARM_MINUTE))

while True:
    # datetime() returns (year, month, day, weekday, hour, minute, second, subsecond)
    now = rtc.datetime()
    hour, minute = now[4], now[5]

    if (hour == ALARM_HOUR and
            minute == ALARM_MINUTE and
            not already_triggered_today(last_trigger_day, now)):

        print("ALARM! {:02d}:{:02d} - flashing display".format(hour, minute))
        last_trigger_day = now[2]
        flash_alarm()

    time.sleep_ms(500)  # check twice per second

