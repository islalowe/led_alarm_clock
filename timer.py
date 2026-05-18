"""
LED Matrix Flashing Countdown Timer
Kitchen timer style: counts down, then flashes until a button is pressed.
Button: GP15 (connect to GND when pressed)
"""

import machine
import max7219
import time

# Countdown config 
COUNTDOWN_MINUTES = 10
COUNTDOWN_SECONDS = 0

# Hardware setup 
spi = machine.SPI(0,
                  sck=machine.Pin(6),
                  mosi=machine.Pin(7))
cs      = machine.Pin(5, machine.Pin.OUT)
display = max7219.Matrix8x8(spi, cs, 4)
display.brightness(15)

button = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
# Button reads LOW when pressed (pulled to GND)

def flash_alarm():
    """Flash at 1 Hz until the button is pressed."""
    print("Timer done! Press button to stop.")
    half_period_ms = 500

    while True:
        # Check button each half-cycle
        if button.value() == 0:
            display.fill(0)
            display.show()
            print("Stopped.")
            break

        display.fill(1)
        display.show()
        time.sleep_ms(half_period_ms)

        if button.value() == 0:
            display.fill(0)
            display.show()
            print("Stopped.")
            break

        display.fill(0)
        display.show()
        time.sleep_ms(half_period_ms)

# Main countdown
total_seconds = COUNTDOWN_MINUTES * 60 + COUNTDOWN_SECONDS
print("Timer started: {:02d}:{:02d}".format(COUNTDOWN_MINUTES, COUNTDOWN_SECONDS))

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
