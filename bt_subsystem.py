from machine import UART, Pin
import utime

ALERT_ALARM = b'A'
ALERT_TIMER = b'T'
ALERT_SUNRISE = b'S'
ALERT_CLEAR = b'C'

try:
    led = Pin(25, Pin.OUT)
except:
    led = Pin("LED", Pin.OUT)

class HC06Bluetooth:
    def __init__(self, baud=9600):
        self._uart = UART(0, baudrate=baud, tx=Pin(12), rx=Pin(13))
        print("[BT] HC-06 subsystem ready on UART0 (GP12/GP13)")

    def send_alert(self, code: bytes) -> None:
        self._uart.write(code + b'\n')
        
        if code == ALERT_CLEAR: label = "CLEAR"
        elif code == ALERT_ALARM: label = "ALARM"
        elif code == ALERT_TIMER: label = "TIMER DONE"
        elif code == ALERT_SUNRISE: label = "SUNRISE"
        else: label = "UNKNOWN"

        print("[BT] Sent -> " + label)
        led.on()
        utime.sleep_ms(100)
        led.off()
