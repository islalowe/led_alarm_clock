# This file is the LCD driver wrapper; handles writing time, alarm status, and mode text to the screen.


import machine
import max7219
from config import SPI_SCK, SPI_MOSI, CS_PIN

spi = machine.SPI(0, sck=machine.Pin(SPI_SCK), mosi=machine.Pin(SPI_MOSI))
cs  = machine.Pin(CS_PIN, machine.Pin.OUT)
display = max7219.Matrix8x8(spi, cs, 4)
display.brightness(15)


from machine import I2C, Pin
import utime

# ─────────────────────────────────────────────
# LCD CONFIGURATION
# ─────────────────────────────────────────────

LCD_I2C_ADDR = 0x27
LCD_I2C_ID   = 0

LCD_SDA_PIN  = 0
LCD_SCL_PIN  = 1

# ─────────────────────────────────────────────


# ── LCD Driver ───────────────────────────────

class I2CLCD:

    LCD_CHR = 1
    LCD_CMD = 0

    BACKLIGHT_ON  = 0x08
    BACKLIGHT_OFF = 0x00

    ENABLE_BIT = 0b00000100

    def __init__(self, i2c, addr=0x27, rows=2, cols=16):

        self.i2c  = i2c
        self.addr = addr

        self.rows = rows
        self.cols = cols

        self.bl = self.BACKLIGHT_ON

        self._init_display()

    def _write_byte(self, data):
        self.i2c.writeto(
            self.addr,
            bytes([data | self.bl])
        )

    def _toggle_enable(self, data):

        utime.sleep_us(500)

        self._write_byte(data | self.ENABLE_BIT)

        utime.sleep_us(500)

        self._write_byte(
            data & ~self.ENABLE_BIT
        )

        utime.sleep_us(500)

    def _send_nibble(self, nibble, mode):

        high = (nibble & 0xF0) | mode

        self._write_byte(high)

        self._toggle_enable(high)

    def _send_byte(self, byte, mode):

        self._send_nibble(
            byte & 0xF0,
            mode
        )

        self._send_nibble(
            (byte << 4) & 0xF0,
            mode
        )

    def _command(self, cmd):
        self._send_byte(cmd, self.LCD_CMD)

    def write_char(self, char):
        self._send_byte(ord(char), self.LCD_CHR)

    def _init_display(self):

        utime.sleep_ms(50)

        for _ in range(3):

            self._send_nibble(
                0x30,
                self.LCD_CMD
            )

            utime.sleep_ms(5)

        self._send_nibble(
            0x20,
            self.LCD_CMD
        )

        utime.sleep_ms(1)

        self._command(0x28)
        self._command(0x0C)
        self._command(0x06)

        self.clear()

    def clear(self):

        self._command(0x01)

        utime.sleep_ms(2)

    def set_cursor(self, col, row):

        row_offsets = [0x00, 0x40]

        self._command(
            0x80 | (col + row_offsets[row])
        )

    def print(self, text):

        for ch in str(text):
            self.write_char(ch)

    def print_line(self, row, text):

        self.set_cursor(0, row)

        text = str(text)

        padded = text + (
            " " * (self.cols - len(text))
        )

        self.print(padded[:self.cols])

    def backlight(self, on):

        self.bl = (
            self.BACKLIGHT_ON
            if on else
            self.BACKLIGHT_OFF
        )

        self._write_byte(0)


# ── Display Manager ──────────────────────────

class DisplayManager:

    def __init__(self):

        i2c = I2C(
            LCD_I2C_ID,
            sda=Pin(LCD_SDA_PIN),
            scl=Pin(LCD_SCL_PIN),
            freq=400_000
        )

        self.lcd = I2CLCD(
            i2c,
            addr=LCD_I2C_ADDR
        )

    # ── Startup ──────────────────────────────

    def startup_screen(self):

        self.lcd.print_line(
            0,
            "  Pico Clock  "
        )

        self.lcd.print_line(
            1,
            "  Starting... "
        )

        utime.sleep_ms(1200)

    # ── Mode Switch ──────────────────────────

    def mode_switch_screen(self, mode):

        if mode == "ALARM":

            self.lcd.print_line(
                0,
                "> ALARM MODE <"
            )

        else:

            self.lcd.print_line(
                0,
                "> TIMER MODE <"
            )

        self.lcd.print_line(
            1,
            "----------------"
        )

        utime.sleep_ms(700)

    # ── Alarm Display ────────────────────────

    def update_alarm(
        self,
        current_time,
        alarm_hour,
        alarm_min,
        alarm_armed,
        state_label
    ):

        armed_indicator = (
            "*" if alarm_armed else " "
        )

        row0 = "[ALM]{} {}".format(
            current_time,
            armed_indicator
        )

        row1 = "A:{:02d}:{:02d} [{:>3}]".format(
            alarm_hour,
            alarm_min,
            state_label
        )

        self.lcd.print_line(0, row0)
        self.lcd.print_line(1, row1)

    # ── Timer Display ────────────────────────

    def update_timer(
        self,
        current_time,
        timer_str,
        state_label
    ):

        row0 = "[TMR]{}".format(
            current_time
        )

        row1 = "T:{} [{:>4}]".format(
            timer_str,
            state_label
        )

        self.lcd.print_line(0, row0)
        self.lcd.print_line(1, row1)
