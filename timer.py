"""
LED Matrix Flashing Countdown Timer
Counts down from a configured duration, then flashes the LED matrix.
Config: set COUNTDOWN_MINUTES below.
"""

import machine
import max7219
import time

# Countdown config 
COUNTDOWN_MINUTES = 1    # how long to count down (minutes)
COUNTDOWN_SECONDS = 0    # additional seconds

# Flash config 
FLASH_ON_MS  = 500
FLASH_OFF_MS = 500

# Display setup 
spi = machine.SPI(0,
                  sck=machine.Pin(6),
                  mosi=machine.Pin(7))
cs      = machine.Pin(5, machine.Pin.OUT)
display = max7219.Matrix8x8(spi, cs, 4)
display.brightness(15)

def flash_alarm():
    TIMEOUT_MINUTES = 10   # alarm stops after this long

    start_ms = time.ticks_ms()
    while True:
        elapsed_ms      = time.ticks_diff(time.ticks_ms(), start_ms)
        elapsed_minutes = elapsed_ms // 60000

        if elapsed_minutes >= TIMEOUT_MINUTES:
            display.fill(0)
            display.show()
            break

        if elapsed_minutes < 2:
            half_period_ms = 500
        elif elapsed_minutes < 4:
            half_period_ms = 250
        else:
            half_period_ms = 125

        display.fill(1)
        display.show()
        time.sleep_ms(half_period_ms)
        display.fill(0)
        display.show()
        time.sleep_ms(half_period_ms)

# Main countdown 
total_seconds = COUNTDOWN_MINUTES * 60 + COUNTDOWN_SECONDS
print("Countdown started: {:02d}:{:02d}".format(COUNTDOWN_MINUTES, COUNTDOWN_SECONDS))

start_ms = time.ticks_ms()

while True:
    elapsed_ms      = time.ticks_diff(time.ticks_ms(), start_ms)
    elapsed_seconds = elapsed_ms // 1000
    remaining       = total_seconds - elapsed_seconds

    if remaining <= 0:
        print("Countdown complete! Flashing display.")
        flash_alarm()
        break

    mins = remaining // 60
    secs = remaining % 60
    print("Time remaining: {:02d}:{:02d}".format(mins, secs), end="\r")
    time.sleep_ms(500)