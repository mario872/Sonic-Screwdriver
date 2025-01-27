"""
import supervisor

supervisor.set_next_code_file('test.py', reload_on_success=True)
supervisor.reload()
exit()
"""

####################################################################################################
# Imports

import time
import board
import adafruit_max1704x
import displayio
from adafruit_display_text import label
from adafruit_display_text.bitmap_label import Label as bmp_label
import terminalio
from adafruit_display_shapes.rect import Rect
from wrappers import MAX17048, IRSENDER, IRRECEIVER, PIEZO, update_position_and_menu, update_menu
from menu import Menu
from font_free_sans_10 import FONT as MONO_8
from digitalio import DigitalInOut, Pull, Direction
import neopixel

####################################################################################################
# Setup devices

i2c = board.I2C() # Global I2C bus

# Setup display
display = board.DISPLAY
display.rotation = 180
# Setup text
text = "HELLO WORLD"
font = terminalio.FONT
color = 0xFFFFFF
text = label.Label(font, text=text, color=color, scale=2, x=6, y=14)
bat_text = bmp_label(font=MONO_8, text="4.20V\n100%", x=200, y=10, color=color, scale=1)

rect = Rect(190, 0, 1, 135, fill=0xFFFFFF)

splash = displayio.Group()
splash.append(text)
splash.append(rect)
splash.append(bat_text)

display.root_group = splash
# That was easy

# Setup the battery monitor
text.text = "Setting up\nbattery monitor"
print("Setting up battery monitor...")
max17 = MAX17048(i2c)

# Setup buttons
text.text = "Setting up\nbuttons"
print("Setting up buttons...")
select_btn = DigitalInOut(board.D5)
select_btn.switch_to_input(pull=Pull.UP)
back_btn = DigitalInOut(board.D6)
back_btn.switch_to_input(pull=Pull.UP)
up_btn = DigitalInOut(board.D9)
up_btn.switch_to_input(pull=Pull.UP)
down_btn = DigitalInOut(board.D11)
down_btn.switch_to_input(pull=Pull.UP)
left_btn = DigitalInOut(board.D10)
left_btn.switch_to_input(pull=Pull.UP)
right_btn = DigitalInOut(board.D12)
right_btn.switch_to_input(pull=Pull.UP)

# Setup IR
text.text = "Setting up\nIR"
print("Setting up IR...")
ir_sender = IRSENDER(board.D13)
ir_receiver = IRRECEIVER(board.A0)

# Setup piezo
text.text = "Setting up\npiezo"
print("Setting up piezo...")
piezo = PIEZO(board.A1)

# Setup UV LED
text.text = "Setting up\nUV LED"
print("Setting up UV LED...")
uv_led = DigitalInOut(board.A5)
uv_led.direction = Direction.OUTPUT
uv_led.value = False

# Setup vibration motor
text.text = "Setting up\nvibration motor"
print("Setting up vibration motor...")
vibration_motor = DigitalInOut(board.A2)
vibration_motor.direction = Direction.OUTPUT
vibration_motor.value = False

# Setup neopixels
text.text = "Setting up\nneopixels"
print("Setting up neopixels...")
pixels = neopixel.NeoPixel(board.A3, 6, brightness=0.2, auto_write=True)
pixels.fill((0, 0, 0))

# Setup menu
menu = Menu(
    {"title": "Menu", "items": [
        {"title": "TV B Gone", "function": lambda: ir_sender.tv_b_gone(text, select_btn, display_neopixel=True, chosen_neopixel=pixels)},
    ]}
)

text.text = "Setup complete"
print("Setup complete")

update_menu(menu, text)
while True:
    update_position_and_menu(menu, text, select_btn, left_btn, right_btn)
    bat_text.text = f"{max17.get_voltage()}V\n{max17.get_percentage()}%"