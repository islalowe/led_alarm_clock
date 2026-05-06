# This file is the LCD driver wrapper; handles writing time, alarm status, and mode text to the screen.


import machine
import max7219
from config import SPI_SCK, SPI_MOSI, CS_PIN

spi = machine.SPI(0, sck=machine.Pin(SPI_SCK), mosi=machine.Pin(SPI_MOSI))
cs  = machine.Pin(CS_PIN, machine.Pin.OUT)
display = max7219.Matrix8x8(spi, cs, 4)
display.brightness(15)
