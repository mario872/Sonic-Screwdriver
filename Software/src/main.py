"""
Copyright (C) 2024  James Glynn

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see https://www.gnu.org/licenses/gpl-3.0.html.
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Imports

# General CircuitPython imports
import board
from digitalio import DigitalInOut, Direction, Pull
import pwmio
import pulseio
from neopixel import NeoPixel, RGB

# General pythonic imports
import time
import random
import array # An array is basically just a computationally faster python list

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# GPIO Setup

vibrator = DigitalInOut(board.GP0)
vibrator.direction = Direction.OUTPUT

r = pwmio.PWMOut(board.GP1)
g = pwmio.PWMOut(board.GP2)
b = pwmio.PWMOut(board.GP3)

pixel = NeoPixel(board.GP16, 1, auto_write=True, pixel_order=RGB) # The neopixel present on the board

piezo = pwmio.PWMOut(board.GP4, variable_frequency=True)

small_button = DigitalInOut(board.GP5)
small_button.direction = Direction.INPUT
small_button.pull = Pull.UP

large_button = DigitalInOut(board.GP6)
large_button.direction = Direction.INPUT
large_button.pull = Pull.UP

led = pwmio.PWMOut(board.GP7)

ir_send = pulseio.PulseOut(board.GP8, frequency=38000, duty_cycle=2**15)
ir_read = pulseio.PulseIn(board.GP9, maxlen=1000, idle_state=True)

# Stop the ir receiver from receiving code and make sure to clear any that it already has
ir_read.pause()
ir_read.clear()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Variables Set Up

mode = 0 #The current mode we are in, modes listed further down

# Setting up colours for the button led
# If you wanted a standard red, you would use (255, 0, 0) but the
# button's values are inverted, and difficult to get right without
# experimenting with precise values

red = (0, 65535, 65535)
green = (65535, 0, 65535)
blue = (65535, 65535, 0)
orange = (30000, 15535, 65535)
yellow = (35535, 5535, 65535)
aqua = (65535, 35535, 15535)
purple = (55535, 65535, 15535)
violet = (35535, 65535, 15535)
white = (0, 0, 0)
black = (65535, 65535, 65535)

colours = [red, green, blue, orange, yellow, aqua, purple, violet, white, black]

neo_red = (255, 0, 0)
neo_green = (0, 255, 0)
neo_blue = (0, 0, 255)
neo_orange = (255, 100, 0)
neo_yellow = (255, 255, 0)
neo_aqua = (0, 255, 100)
neo_purple = (150, 0, 255)
neo_violet = (255, 0, 100)
neo_white = (255, 255, 255)
neo_black = (0, 0, 0)

neo_colours = [neo_red, neo_green, neo_blue, neo_orange, neo_yellow, neo_aqua, neo_purple, neo_violet, neo_white, neo_black]

command = array.array('H', [6500, 0, 6500, 0]) # If the user wants to send the current command, without capturing a command previously in mode one, it will fail, this is a 'default' value

stealth = not small_button.value # Because this is reversed to due the button being conneced to ground usually, if it is pressed it should enable stealth mode, causing a False value to enable stealth mode

freq = (700, 950, 35) # The frequencies to step between after sending the ir code. The tuple if the start value, the end value, and the amount to step between each time 

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Functions Set Up

def largebtnval():
    "This returns the opposite of the current large button value"
    return not large_button.value
def smallbtnval():
    "This returns the opposite of the current small button value"
    return not small_button.value

def set_colour(colour, button=True, neopixel=True):
    "This sets the colour of the button and neopixel based on a tuple in two lists"
    
    if button:
        r.duty_cycle = colour[0]
        g.duty_cycle = colour[1]
        b.duty_cycle = colour[2]
    
    if neopixel:
        pixel.fill(neo_colours[colours.index(colour)])

def led_ir_indicate(current_command=None):
    """This blinks the led on and off the same way that the ir
    led would be blinked on and off when sending the infrared codes"""
    
    global led
    led.deinit()
    led = pulseio.PulseOut(board.GP7, duty_cycle=2**15)
    if current_command == None:
        led.send(command)
    else:
        led.send(current_command)
    led.deinit()
    led = pwmio.PWMOut(board.GP7)

def rise_and_fall():
    """
    This sets
    """
    for i in range(freq[0], freq[1], freq[2]):
        led.duty_cycle = random.randint(20000, 65535)
        piezo.frequency = i
        time.sleep(0.01)
    for i in reversed(range(freq[0], freq[1], freq[2])):
        led.duty_cycle = random.randint(20000, 65535)
        piezo.frequency = i
        time.sleep(0.005)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Modes Set Up

def dynamic_mode():
    """
    This mode can clone and send an ir remote codes to other ir devices
    """
    global mode
    global command

    set_colour(orange)
    
    if smallbtnval():
        set_colour(violet)
        ir_read.resume()
        
        while smallbtnval():
            time.sleep(0.01)
            if largebtnval():
                ir_read.pause()
                ir_read.clear()
                
                while largebtnval():
                    set_colour(white)
                    time.sleep(0.1)
                    set_colour(red)
                    time.sleep(0.1)
                    
                mode += 1
                return
            
        time.sleep(0.1) #The following fwe lines prevent accidental presses of the small button
        if smallbtnval:
            pass
        
        ir_read.pause()
        
        if len(ir_read) == 0: #This block makes sure that the command variable is set properly, and not to None
            command = array.array('H', [6500, 0, 6500, 0])
        else:
            command = array.array('H', [ir_read[x] for x in range(len(ir_read))])
            led_ir_indicate() # This flashes out the ir code using the main led, so the user knows an ir code has been captured
            
        print(f'Dynamic mode command captured is {command}')
    
        ir_read.clear()
        
    elif largebtnval():
        ir_send.send(command)
        print(f'Dynamic mode command sent is {command}')
        
        if not stealth:
            vibrator.value = True
            piezo.duty_cycle = 60000
            
        while largebtnval():
            if not stealth:
                rise_and_fall()
            else:
                set_colour(black, neopixel=False)
                time.sleep(0.3)
                set_colour(red, neopixel=False)
                time.sleep(0.3)
                set_colour(orange, neopixel=False)
                
        vibrator.value = False
        led.duty_cycle = 0
        piezo.duty_cycle = 0
        
def annoying_mode():
    """
    This mode makes a high pitched annoying tone so long as the button is being held down
    """
    
    global mode
    if smallbtnval():
        while smallbtnval():
            if largebtnval():
                while largebtnval():
                    set_colour(white)
                    time.sleep(0.1)
                    set_colour(red)
                    time.sleep(0.1)
                mode += 1
                return
            
    elif largebtnval():
        led.duty_cycle = 65535
        piezo.duty_cycle = 60000
        while largebtnval():
            piezo.frequency = 1000
        piezo.duty_cycle = 0
        led.duty_cycle = 0
        
def tv_b_gone_mode():
    """
    The orginal code from this file is from https://learn.adafruit.com/circuitpython-tv-zapper-with-circuit-playground-express/gemma-m0-variant
    and has been modifed to work more effectively for the Sonic Screwdiver
    
    It was originally licensed under the MIT license by John Edgar Park for Adafruit Industries in 2018
    """
    
    global mode
    set_colour(purple)
    
    while not largebtnval(): # Wait until the large button is pressed before starting
        pass

    f = open("/codes.txt", "r") # Read the list of codes
    for line in f:
        code = eval(line)
        print(f'TV B GONE mode code sent is{code}')
        if not stealth: # If it's not stealth mode then flash the main led, piezo, and vibrator on and off
            led.duty_cycle = 65535
            vibrator.value = True
            piezo.duty_cycle = 60000
            rise_and_fall()
            vibrator.value = False
            led.duty_cycle = 0
            piezo.duty_cycle = 0
            
        else: # Else, just flash the button's led
            set_colour(black, neopixel=False)
            time.sleep(0.1)
            set_colour(red, neopixel=False)
            time.sleep(0.1)
            set_colour(purple, neopixel=False)
        # If this is a repeating code, extract details
        try:
            repeat = code['repeat']
            delay = code['repeat_delay']
        except KeyError:  # By default, repeat once only!
            repeat = 1
            delay = 0
            
        # The table holds the on/off pairs
        table = code['table']
        pulses = []
        # Read through each indexed element
        for i in code['index']:
            pulses += table[i]  # And add to the list of pulses
        pulses.pop()  # Remove one final 'low' pulse

        for i in range(repeat):
            ir_send.send(array.array('H', pulses))
            time.sleep(delay)
        led.duty_cycle = 0
        time.sleep(code['delay'])

        if largebtnval(): # If the large button was pressed, then switch to the next mode
            while largebtnval():
                set_colour(white)
                time.sleep(0.1)
                set_colour(red)
                time.sleep(0.1)
            mode += 1
            f.close()
            return
        
    f.close() 

def permanent_bank_storage_mode():
    """
    This mode has eight permenant storage banks, based on colour, that can hold one code per bank
    """
    
    bank = 0 # This is like the mode vairable, but for only this function
    set_colour(aqua, neopixel=False)
    
    with open('bank.txt', 'r') as banks_txt: # Open the banks.txt file, that holds the previously encoded values
        banks = banks_txt.readlines()
        if len(banks) < 7: # If there is not 8 banks, then add banks
            while len(banks) < 8: # Until there are 8 banks total
                banks.append('6500,0,6500,0') # The pulses are stored as strings delimited by commas, for easy conversion to integers later
                
        for item in range(len(banks)):
            current_bank = banks[item].split(',') # Split the string into a list based on the commas
            for string in range(len(current_bank)): # For each string, convert it to an integer, and save it as an integer in the same list
                current_bank[string] = int(current_bank[string])
            banks[item] = current_bank # Add the converted bank to the program's banks variable
            
    while True: #This is the final mode, and is insde it's own infinite loop
        set_colour(aqua, neopixel=False)
        break_up = False
        set_colour(colours[bank], button=False)
        if smallbtnval(): # Programming mode
            ir_read.clear()
            ir_read.resume()
            while smallbtnval():
                set_colour(violet, neopixel=False)
                if largebtnval(): # To switch banks hold the small button and large button at the smae time
                    if not bank == 7:
                        bank += 1
                    else:
                        bank = 0
                    while largebtnval():
                        set_colour(white)
                        time.sleep(0.1)
                        set_colour(red)
                        time.sleep(0.1)
                    break_up = True
                    ir_read.pause()
                    ir_read.clear()
                    
            if break_up:
                continue
            
            ir_read.pause()
            
            if [ir_read[x] for x in range(len(ir_read))] == []: # Is ir_read empty?
                banks[bank] = [6500, 0, 6500, 0] # If so, set it to a default value
            else:
                banks[bank] = [ir_read[x] for x in range(len(ir_read))]
            
            led_ir_indicate(array.array('H', banks[bank])) # Use the main LED to show the user what was captured by the receiver
            
            with open('bank.txt', 'w') as banks_txt: # Every time the ir receiver receives something, it is saved in the banks.txt file
                for item in banks: # This loop converts the integers in the program's bamk variable to a stringed list that's comma delimited
                    code = ''
                    for pulse in item:
                        code += str(pulse) + ','
                    code = code[:-1]
                    if banks.index(item) == 7:
                        banks_txt.write(code)
     