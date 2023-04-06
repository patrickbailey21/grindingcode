from sense_hat import SenseHat
from time import sleep, strftime, time
import subprocess

sense = SenseHat()
sense.low_light = True

# Set up colors
white = (125, 125, 125)
red = (255, 0, 0)
green = (0, 255, 0)

# Set up variables
display_mode = 0   # 0 = time, 1 = temperature, 2 = humidity
last_display_mode = 0  # keep track of last display mode
last_active_time = time() # keep track of the last active time
inactive_time = 4  # number of seconds to display the last display mode before switching back to the time display

# Define functions
def get_temperature():
    #Averages temp from humidity and pressure due to cpu putting off heat
    output = subprocess.check_output("cat /sys/class/thermal/thermal_zone0/temp", shell=True)
    cpu = int(output)/1000
    avg_temp = (sense.get_temperature_from_pressure() + sense.get_temperature_from_humidity()) / 2
    temp_c = avg_temp - (cpu - avg_temp)
    temp_f = (temp_c * 9/5) +32
    temp = temp_f
    return round(temp, 1)

def get_humidity():
    humidity = sense.get_humidity()
    return round(humidity, 1)

def display_time():
    # Get the current time
    time_str = strftime("%H:%M")

    # Display the time
    sense.show_message(time_str, text_colour=white, scroll_speed=0.1)

def display_temp():
    # Get the current temperature
    temp = get_temperature()

    # Display the temperature
    sense.show_message("{0} F".format(temp), text_colour=red, scroll_speed=0.1)

def display_humidity():
    # Get the current humidity
    humidity = get_humidity()

    # Display the humidity
    sense.show_message("{0} %".format(humidity), text_colour=green, scroll_speed=0.1)

# Listen for joystick events
while True:
    for event in sense.stick.get_events():
        if event.action == "pressed":
            last_active_time = time() # record the time of the last active event
            if event.direction == "middle":
                # Update the display mode
                display_mode = (display_mode + 1) % 3
                
                # Clear the LED array
                sense.clear()
                
                # Display the appropriate mode
                if display_mode == 0:
                    display_time()
                elif display_mode == 1:
                    display_temp()
                elif display_mode == 2:
                    display_humidity()
                    
            elif event.direction == "up":
                if display_mode == 1:
                    # Display the temperature
                    display_temp()
                elif display_mode == 2:
                    # Display the humidity
                    display_humidity()
                    
            # Store the last display mode
            last_display_mode = display_mode
                    
        elif event.action == "released":
            # Switch to the last display mode if it's been less than inactive_time since the last active event
            if time() - last_active_time < inactive_time:
                display_mode = last_display_mode
                
            # Clear the LED array when joystick is released
            sense.clear()
            
    # If the joystick is not being pressed, display the last display mode for inactive_time seconds before switching back to the time display
    if sense.stick.get_events() == []:
        elapsed_time = time() - last_active_time
        if elapsed_time < inactive_time and last_display_mode != 0:
            if last_display_mode == 1:
                display_temp()
            elif last_display_mode == 2:
                display_humidity()
        else:
            display_time()
            last_display_mode = 0
            
