# This file controls the LED array via PWM; handles the sunrise gradual brighten, 
# the escalating flash sequence, and brightness adjustment from the photoresistor/potentiometer.


import time
from display import display
from config import FLASH_COUNT, FLASH_ON_MS, FLASH_OFF_MS

def flash_alarm():
    count = 0
    while FLASH_COUNT == 0 or count < FLASH_COUNT:
        display.fill(1)
        display.show()
        time.sleep_ms(FLASH_ON_MS)
        display.fill(0)
        display.show()
        time.sleep_ms(FLASH_OFF_MS)
        count += 1
