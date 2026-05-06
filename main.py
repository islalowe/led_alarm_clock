# This file is the entry point; runs on boot and contains the main loop, clock vs. alarm mode switching, and ties all the files together
# Entry point — imports and runs everything


import time
from config import ALARM_HOUR, ALARM_MINUTE
from clock import get_time
from led_control import flash_alarm

last_trigger_day = -1

while True:
    hour, minute = get_time()
    if hour == ALARM_HOUR and minute == ALARM_MINUTE:
        flash_alarm()
    time.sleep_ms(500)
