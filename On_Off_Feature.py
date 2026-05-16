from machine import Pin, UART
import utime

# Initialize Bluetooth (UART1) at standard 9600 baud rate
bt = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

# 0 = Clock Mode, 1 = Alarm Mode
current_state = 0 


while True:
    if bt.any():
        # Read the message from tablet
        # .decode() turns the 'bytes' into a readable string
        data = bt.read().decode('utf-8').strip()
        
        if data == 'A':
            current_state = 1
            print("Mode Switched: ALARM")
        elif data == 'C':
            current_state = 0
            print("Mode Switched: CLOCK")
            
    # This is where OLED code goes
    if current_state == 0:
        # Show Clock
        pass
    else:
        # Show Alarm Setup
        pass

    utime.sleep(0.1)