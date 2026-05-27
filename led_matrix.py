from machine import Pin, SPI, ADC
import utime
import max7219
from config import LDR_PIN, LDR_THRESHOLD, SUNRISE_START_PCT, FLASH_TIMEOUT_MINS

ldr = ADC(Pin(LDR_PIN))

def get_sunrise_start_pct():
    reading = ldr.read_u16()
    print("LDR reading:", reading)
    return 20 if reading >= LDR_THRESHOLD else 10

class LEDMatrix:
    def __init__(self, spi_id, sck_pin, mosi_pin, cs_pin, num_chips):
        spi = SPI(spi_id, sck=Pin(sck_pin), mosi=Pin(mosi_pin))
        cs  = Pin(cs_pin, Pin.OUT)
        self._m = max7219.Matrix8x8(spi, cs, num_chips)
        self._m.brightness(0)
        self._m.fill(0)
        self._m.show()

        self._sunrise_active    = False
        self._sunrise_start_ms  = 0
        self._sunrise_dur_ms    = 0
        self._sunrise_start_pct = SUNRISE_START_PCT

        self._flash_active   = False
        self._flash_on       = False
        self._flash_next_ms  = 0
        self._flash_start_ms = 0

    def _set_brightness_pct(self, pct):
        level = max(0, min(15, int((pct / 100.0) * 15)))
        self._m.brightness(level)

    def start_sunrise(self, duration_minutes):
        self._sunrise_dur_ms    = duration_minutes * 60 * 1000
        self._sunrise_start_ms  = utime.ticks_ms()
        self._sunrise_active    = True
        self._sunrise_start_pct = get_sunrise_start_pct()
        print("Sunrise start brightness:", self._sunrise_start_pct, "%")
        self._m.fill(1)
        self._set_brightness_pct(self._sunrise_start_pct)
        self._m.show()

    def stop_sunrise(self):
        self._sunrise_active = False
        self._m.fill(0)
        self._set_brightness_pct(0)
        self._m.show()

    def sunrise_active(self):
        return self._sunrise_active

    def start_flash(self):
        self._flash_active   = True
        self._flash_on       = True
        self._flash_start_ms = utime.ticks_ms()
        self._flash_next_ms  = utime.ticks_ms()
        self._m.fill(1)
        self._set_brightness_pct(100)
        self._m.show()

    def stop_flash(self):
        self._flash_active = False
        self._flash_on     = False
        self._m.fill(0)
        self._m.show()

    def flash_active(self):
        return self._flash_active

    def update(self):
        now = utime.ticks_ms()

        if self._sunrise_active:
            elapsed  = utime.ticks_diff(now, self._sunrise_start_ms)
            progress = elapsed / self._sunrise_dur_ms
            if progress >= 1.0:
                self._set_brightness_pct(100)
                self._m.fill(1)
                self._m.show()
            else:
                brightness = self._sunrise_start_pct + ((100 - self._sunrise_start_pct) * progress)
                self._set_brightness_pct(brightness)

        if self._flash_active:
            elapsed_mins = utime.ticks_diff(now, self._flash_start_ms) // 60000
            if elapsed_mins >= FLASH_TIMEOUT_MINS:
                self.stop_flash()
                return
            half_period = 500 if elapsed_mins < 2 else 250 if elapsed_mins < 4 else 125
            if utime.ticks_diff(now, self._flash_next_ms) >= 0:
                self._flash_on = not self._flash_on
                self._m.fill(1 if self._flash_on else 0)
                self._m.show()
                self._flash_next_ms = utime.ticks_add(now, half_period)
