 # This file contains timekeeping logic; tracks current time, alarm time, and handles the alarm trigger condition.

#TODO change this file onve we incorporate RTC module

import machine
rtc = machine.RTC()

def set_time(year, month, day, hour, minute, second=0):
    rtc.datetime((year, month, day, 0, hour, minute, second, 0))

def get_time():
    now = rtc.datetime()
    return now[4], now[5]  # returns (hour, minute)
