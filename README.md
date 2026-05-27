# led_alarm_clock
### A deaf-friendly alarm clock built on a Pico board that uses visual feedback to wake up the user.

### Feature 1: LED Flashing When Alarm Goes Off  
When the alarm triggers, an **8×32 LED matrix** flashes to provide a high-intensity visual cue.
- Flashing frequency starts at **1 Hz** and doubles every 2 minutes if not deactivated, reaching a maximum urgency cap at **4 Hz**
- LED brightness is auto-adjusted via an **LDR sensor**. It employs full brightness (100%) in bright rooms, and reduced (70%) in dark rooms to reduce excessive glare

### Feature 2: Display Screen 
A **1602 LCD** shows the current time, alarm time, and alarm status (ON / OFF).
 
### Feature 3: Button Controls  
Three buttons handle all interaction:
- Set the current time
- Set the alarm time
- Stop the alarm once triggered
 
### Feature 4: On and Off System Alarm System  
Turns the alarm system ON and OFF. There is Clock Mode with just the time display and Alarm Mode where the user can set and activate an alarm clock. 
A Manual Switch is used to physically control the power state and toggle between Clock Mode and Alarm Mode to ensure the system is not drawing power when not in use. 
 
### Feature 5: A Sunrise Feature 
For the sunrise alarm, the 8x32 LED matrix slowly increases in brightness over a span of 10 minutes to gradually wake the user in a way that simulates a natural sunrise. 
The sunrise sequence begins exactly 10 minutes before the set alarm time, starting from 10% and increasing linearly to 100% brightness by the alarm time. 
Once the alarm time is reached, the system transitions from sunrise mode into the full flashing alarm mode. 
An LDR (Light Dependent Resistor) sensor placed on the top/front of the device detects ambient room lighting and adjusts brightness levels automatically. 
- In low-light conditions, the sunrise feature begins at 10% brightness and increases gradually over 10 minutes until reaching 100% brightness at the alarm time to prevent excessive glare. 
- In brighter environments, the LED output begins at 20% brightness and increases at twice the rate, still reaching 100% brightness by the alarm time to remain clearly visible to the user. 

### Libraries used:
| File | Purpose | Source |
|------|---------|--------|
| `lcd_api.py` / `pico_i2c_lcd.py` | I2C LCD driver | [dhylands/micropython-i2c-lcd](https://github.com/dhylands/micropython-i2c-lcd) |
| `max7219.py` | LED matrix driver | MAX72XX community lib |
