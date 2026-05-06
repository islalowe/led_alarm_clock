 # This file contains timekeeping logic; tracks current time, alarm time, and handles the alarm trigger condition.


import machine

rtc = machine.RTC()

def set_time(year, month, day, weekday, hour, minute, second=0):
    rtc.datetime((year, month, day, weekday, hour, minute, second, 0))

def get_time():
    # returns (year, month, day, weekday, hour, minute, second, subsecond)
    return rtc.datetime()
