from machine import Pin, I2C
import ssd1306
import time

# ===== HARDWARE SETUP =====
# I2C for SSD1306 (using GP0=SDA, GP1=SCL)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Buttons (GP13, GP14, GP15)
BTN_DEC = 13    # Decrement button - GP13
BTN_INC = 14    # Increment button - GP14
BTN_MODE = 15   # Mode button - GP15

btn_dec = Pin(BTN_DEC, Pin.IN, Pin.PULL_UP)
btn_inc = Pin(BTN_INC, Pin.IN, Pin.PULL_UP)
btn_mode = Pin(BTN_MODE, Pin.IN, Pin.PULL_UP)

# ===== TIME VARIABLES =====
hours = 0
minutes = 0
seconds = 0

# ===== BUTTON DEBOUNCING =====
last_press = 0
debounce_ms = 200

# ===== SETUP STATE =====
setup_mode = True  # Start in setup mode
edit_field = 1     # 1=hours, 2=minutes
clock_running = False

def check_button(pin):
    """Check if button is pressed (returns True once per press)"""
    global last_press
    now = time.ticks_ms()
    if pin.value() == 0 and time.ticks_diff(now, last_press) > debounce_ms:
        last_press = now
        # Wait for button release
        while pin.value() == 0:
            time.sleep_ms(10)
        return True
    return False

def draw_setup_screen():
    """Draw the time setup screen"""
    oled.fill(0)
    
    # Title
    oled.text("SET CLOCK TIME", 20, 0)
    oled.hline(0, 10, 128, 1)
    
    # Time display
    time_str = f"{hours:02d}:{minutes:02d}"
    x = (120 - (len(time_str) * 8)) // 2
    oled.text(time_str, x, 25)
    
    # Highlight active field
    if edit_field == 1:
        # Highlight hours with underline
        oled.hline(x, 33, 16, 1)
        oled.text("^", x + 4, 35)
    else:
        # Highlight minutes with underline
        oled.hline(x + 27, 33, 16, 1)
        oled.text("^", x + 31, 35)
    
    # Instructions
    oled.text("INC/DEC: Change", 5, 43)
    oled.text("MODE: Next Field", 0, 53)
    
    oled.show()

def draw_start_screen():
    """Draw the screen asking to start the clock"""
    oled.fill(0)
    
    oled.text("TIME SET READY", 7, 15)
    oled.hline(0, 25, 128, 1)
    
    time_str = f"{hours:02d}:{minutes:02d}:00"
    x = (128 - (len(time_str) * 8)) // 2
    oled.text(time_str, x, 38)
    
    oled.text("MODE to START", 15, 55)
    
    oled.show()

def draw_running_clock():
    """Draw the running clock display"""
    oled.fill(0)
    
    # Title
    oled.text("DIGITAL CLOCK", 18, 0)
    oled.hline(0, 10, 128, 1)
    
    # Time (centered)
    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    x = (128 - (len(time_str) * 8)) // 2
    oled.text(time_str, x, 28)
    
    # AM/PM
    ampm = "AM" if hours < 12 else "PM"
    oled.text(ampm, 105, 28)
    
    # Indicator
    oled.text("RUNNING", 45, 52)
    
    oled.show()

# ===== INITIAL SETUP PHASE =====
print("=== CLOCK SETUP MODE ===")
print("Use INC/DEC to change values")
print("Press MODE to switch between Hours/Minutes")

draw_setup_screen()

# Setup loop
while setup_mode:
    # Handle MODE button (switch between hours/minutes)
    if check_button(btn_mode):
        if edit_field == 1:
            edit_field = 2
            print("Editing MINUTES")
        else:
            # Exit setup and go to start screen
            setup_mode = False
            print("Setup complete! Ready to start")
            break
        draw_setup_screen()
    
    # Handle INCREMENT button
    if check_button(btn_inc):
        if edit_field == 1:  # Hours
            hours = (hours + 1) % 24
            print(f"Hours: {hours:02d}")
        else:  # Minutes
            minutes = (minutes + 1) % 60
            print(f"Minutes: {minutes:02d}")
        draw_setup_screen()
    
    # Handle DECREMENT button
    if check_button(btn_dec):
        if edit_field == 1:  # Hours
            hours = (hours - 1) % 24
            print(f"Hours: {hours:02d}")
        else:  # Minutes
            minutes = (minutes - 1) % 60
            print(f"Minutes: {minutes:02d}")
        draw_setup_screen()
    
    time.sleep_ms(50)

# ===== READY TO START SCREEN =====
draw_start_screen()
print("\n=== READY TO START ===")
print(f"Set time: {hours:02d}:{minutes:02d}:00")
print("Press MODE to start clock")

# Wait for MODE to start clock
while True:
    if check_button(btn_mode):
        break
    time.sleep_ms(50)

# ===== CLOCK RUNNING PHASE =====
seconds = 0
clock_running = True
last_second = time.ticks_ms()
update_display = True

print("\n=== CLOCK STARTED ===")
print(f"Starting from: {hours:02d}:{minutes:02d}:00")
print("Press MODE to edit time (will pause clock)")

draw_running_clock()

# Main clock loop with pause functionality
while True:
    now = time.ticks_ms()
    
    # Update time every second (only if clock is running)
    if clock_running and time.ticks_diff(now, last_second) >= 1000:
        last_second = now
        seconds += 1
        
        if seconds >= 60:
            seconds = 0
            minutes += 1
            if minutes >= 60:
                minutes = 0
                hours += 1
                if hours >= 24:
                    hours = 0
        update_display = True
        print(f"Time: {hours:02d}:{minutes:02d}:{seconds:02d}")
    
    # Handle MODE button (pause and edit)
    if check_button(btn_mode):
        if clock_running:
            # Pause clock and enter edit mode
            clock_running = False
            edit_field = 1
            print("\n*** CLOCK PAUSED - EDIT MODE ***")
            
            # Edit loop while paused
            paused = True
            while paused:
                # Draw paused edit screen
                oled.fill(0)
                oled.text("EDIT TIME (PAUSED)", 12, 0)
                oled.hline(0, 10, 128, 1)
                
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                x = (128 - (len(time_str) * 8)) // 2
                oled.text(time_str, x, 25)
                
                # Highlight active field
                if edit_field == 1:
                    oled.hline(x, 33, 16, 1)
                    oled.text("^", x + 4, 35)
                else:
                    oled.hline(x + 27, 33, 16, 1)
                    oled.text("^", x + 31, 35)
                
                oled.text("MODE: Next/Save", 5, 52)
                oled.show()
                
                # Handle buttons in edit mode
                if check_button(btn_mode):
                    if edit_field == 1:
                        edit_field = 2
                        print("Editing MINUTES")
                    else:
                        # Exit edit mode and resume
                        paused = False
                        clock_running = True
                        last_second = time.ticks_ms()  # Reset timing
                        print("*** CLOCK RESUMED ***")
                        print(f"New time: {hours:02d}:{minutes:02d}:{seconds:02d}")
                    draw_running_clock()
                    update_display = True
                
                if check_button(btn_inc):
                    if edit_field == 1:
                        hours = (hours + 1) % 24
                        print(f"Hours: {hours:02d}")
                    else:
                        minutes = (minutes + 1) % 60
                        print(f"Minutes: {minutes:02d}")
                    seconds = 0
                
                if check_button(btn_dec):
                    if edit_field == 1:
                        hours = (hours - 1) % 24
                        print(f"Hours: {hours:02d}")
                    else:
                        minutes = (minutes - 1) % 60
                        print(f"Minutes: {minutes:02d}")
                    seconds = 0
                
                time.sleep_ms(50)
            
            update_display = True
        else:
            # If already editing, this is handled above
            pass
    
    # Refresh display if needed
    if update_display and clock_running:
        draw_running_clock()
        update_display = False
    
    time.sleep_ms(10)