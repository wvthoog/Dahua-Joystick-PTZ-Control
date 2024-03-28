import requests
from requests.auth import HTTPDigestAuth
import pygame
import time

'''
right		axis0 +		arg1
left		axis0 -		arg1
down		axis1 +		arg2
up		    axis1 -		arg2
zoomout		axis4 +		arg3
zoonin		axis4 -		arg3
duration				arg4

x_button	    0
square_button	3
triangle_button	2
circle_button	1
'''

# Initialize Pygame
pygame.init()
pygame.joystick.init()

# Initialize joystick
joystick_count = pygame.joystick.get_count()
if joystick_count == 0:
    print("No joystick found. Exiting...")
    pygame.quit()
    quit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

# Camera settings
ip = '192.168.2.21'         # change
username = 'admin'          # change
password = '12345678910'    # change
channel = 1

# Url variables
base_url = f'http://{ip}/cgi-bin/ptz.cgi?action=start&code='
ptz_url = f'{base_url}Continuously&channel={channel}'
preset_url = f'{base_url}GotoPreset&channel=1&arg1=0&arg2={0}&arg3=0'

# Joystick settings
threshold = 0.1
movement_multiplier = 10
zoom_speed_multiplier = 100
x_button = 0
square_button = 3
triangle_button = 2
circle_button = 1

# Default command with all zeros for stop
default_command = {'arg1': 0, 'arg2': 0, 'arg3': 0, 'arg4': 0}

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                # Get the axis values
                axis_x = joystick.get_axis(0)  # Axis for left/right
                axis_y = joystick.get_axis(1)  # Axis for up/down
                axis_zoom_in_out = joystick.get_axis(4)  # Axis for zoom in/zoom out

                # Update the command based on axis values
                command = default_command.copy()
                command['arg1'] = int(axis_x * movement_multiplier) if axis_x > threshold or axis_x < -threshold else 0
                command['arg2'] = -int(axis_y * movement_multiplier) if axis_y > threshold or axis_y < -threshold else 0
                command['arg3'] = -int(axis_zoom_in_out * zoom_speed_multiplier) if axis_zoom_in_out > threshold or axis_zoom_in_out < -threshold else 0

            # Handle button press events
            elif event.type == pygame.JOYBUTTONDOWN:
                # Get the button that was pressed
                button_pressed = event.button

                # Define actions for each button
                if button_pressed == x_button:  # X Button
                    print("X Button pressed. Performing preset action...")
                    preset_number = 1

                elif button_pressed == circle_button:  # Circle Button
                    print("Circle Button pressed. Performing preset action...")
                    preset_number = 4

                elif button_pressed == triangle_button:  # Triangle Button
                    print("Triangle Button pressed. Performing preset action...")
                    preset_number = 3

                elif button_pressed == square_button:  # Square Button 
                    print("Square Button pressed. Performing preset action...")
                    preset_number = 2

                # Construct the URL for Preset command
                preset_url = f'{base_url}GotoPreset&channel=1&arg1=0&arg2={preset_number}&arg3=0'

                # Send the Preset command to the camera
                response = requests.get(preset_url, auth=HTTPDigestAuth(username, password))
                if response.status_code != 200:
                    print("Failed to send Preset command. Reason:", response.text.split('\n')[1])

            else:
                command = default_command.copy()  # Stop if no input

        # Construct the URL for PTZ command
        command_url = ptz_url
        for arg, value in command.items():
            command_url += f"&{arg}={value}"

        # Send the PTZ command to the camera
        response = requests.get(command_url, auth=HTTPDigestAuth(username, password))
        if response.status_code != 200:
            print("Failed to send PTZ command.")

        time.sleep(0.1)  # Add a delay to avoid overwhelming the camera

except KeyboardInterrupt:
    print("Exiting...")
    pygame.quit()
