# led_alarm_clock
A deaf-friendly alarm clock built on a Pico board that uses visual feedback to wake up the user.


lcd_api.py and pico_i2c_lcd.py: community library files for driving an I2C LCD. From T-Display / dhylands repo on GitHub.
matrix library: MAX72XX




Feature 1: LED Flashing When Alarm Goes Off 
An 8x32 LED matrix flashes when the alarm is triggered to provide a high-intensity visual cue. 
The flashing frequency begins at 1 Hz and doubles every 2 minutes if the alarm is not deactivated, reaching a maximum urgency cap of 4 Hz. 
LED brightness during flashing alarm mode is adjusted using an LDR sensor to maintain strong visibility (100% brightness) in bright environments while reducing excessive glare (70% brightness) in dark rooms. 
 
Feature 2: Display Screen 
A 0.96-inch OLED screen display shows the current time, alarm time, and whether the alarm is ON or OFF. 
 
Feature 3: Button Controls  
Used to set current time. 
Used to set alarm time. 
Used to stop the alarm once triggered.  
 
Feature 4: On and Off System Alarm System  
Turns the alarm system ON and OFF. There is Clock Mode with just the time display and Alarm Mode where the user can set and activate an alarm clock. 
A Manual Switch is used to physically control the power state and toggle between Clock Mode and Alarm Mode to ensure the system is not drawing power when not in use. 
 
Feature 5: A Sunrise Feature 
For the sunrise alarm, the 8x32 LED matrix slowly increases in brightness over a span of 10 minutes to gradually wake the user in a way that simulates a natural sunrise. 
The sunrise sequence begins exactly 10 minutes before the set alarm time, starting at 0% brightness and increasing linearly to 100% brightness by the alarm time. 
Once the alarm time is reached, the system transitions from sunrise mode into the full flashing alarm mode. 
An LDR (Light Dependent Resistor) sensor placed on the top/front of the device detects ambient room lighting and adjusts brightness levels automatically. 
In low-light conditions, the sunrise feature begins at 10% brightness and increases gradually over 10 minutes until reaching 100% brightness at the alarm time to prevent excessive glare. 
In brighter environments, the LED output begins at 20% brightness and increases at twice the rate, still reaching 100% brightness by the alarm time to remain clearly visible to the user. 
