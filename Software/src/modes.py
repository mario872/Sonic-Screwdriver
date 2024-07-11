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
from board import *
from digitalio import DigitalInOut, Direction, Pull
import pwmio
import pulseio
from neopixel import NeoPixel, RGB
import keypad
import simpleio

# General pythonic imports
import time
import random
import json
import array  # An array is basically just a computationally faster python list

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# GPIO Setup

with open('config.json', 'r') as config_json: # Opens that config file to check which GPIO to allocate
    config = json.loads(config_json.read()) # Convert the JSON to a Python dictionary

for pin in config['pins']:
    if pin['type'] == 'digitalin': # The type of the pin indicates what is should be set as in the program
        # Globals is a wierd part of Python, it returns all of the global variables, and allows you to set global variables using a string
        globals()[pin['name']] = keypad.Keys([globals()[pin['pin']]], value_when_pressed=pin['value_when_pressed'],
                                             pull=pin['pull'])
        # This sets the name set in the config as a global variable as a Keypad with only one button on it.
        # The Keypad library checks for changes and debouncing in the background.

    elif pin['type'] == 'digitalout':
        globals()[pin['name']] = DigitalInOut(globals()[pin['pin']])
        globals()[pin['name']].direction = Direction.OUTPUT

    elif pin['type'] == 'pwmout':
        if pin['variable_frequency']:
            if pin['name'] == 'piezo':
                piezo_pin = pin['pin']
            globals()[pin['name']] = pwmio.PWMOut(globals()[pin['pin']], variable_frequency=True)
        else:
            globals()[pin['name']] = pwmio.PWMOut(globals()[pin['pin']])

    elif pin['type'] == 'pulseout':
        globals()[pin['name']] = pulseio.PulseOut(globals()[pin['pin']], frequency=38000, duty_cycle=2 ** 15)

    elif pin['type'] == 'pulsein':
        globals()[pin['name']] = pulseio.PulseIn(globals()[pin['pin']], maxlen=1000, idle_state=True)

    elif pin['type'] == 'neopixel':
        globals()[pin['name']] = NeoPixel(globals()[pin['pin']], 1, auto_write=True, pixel_order=RGB)

# Stop the ir receiver from receiving code and make sure to clear any that it already has
ir_read.pause()
ir_read.clear()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Variables Set Up

mode = 0  # The current mode we are in, modes listed further down
previous_mode = mode

# Setting up colours for the button led
# If you wanted a standard red, you would use (255, 0, 0), but the
# button's rgb values are inverted, and difficult to get right without
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

# These are the colours for the NeoPixel,
# which are just normal rgb values

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

neo_colours = [neo_red, neo_green, neo_blue, neo_orange, neo_yellow, neo_aqua, neo_purple, neo_violet, neo_white,
               neo_black]

# Below is a list of all the possible notes that can be programmed to play, with their pitch listed next to them
notes = {'N':0,'C0':16.35,'C#0/Db0':17.32,'D0':18.35,'D#0/Eb0':19.45,'E0':20.6,'F0':21.83,'F#0/Gb0':23.12,'G0':24.5,'G#0/Ab0':25.96,'A0':27.5,'A#0/Bb0':29.14,'B0':30.87,'C1':32.7,'C#1/Db1':34.65,'D1':36.71,'D#1/Eb1':38.89,'E1':41.2,'F1':43.65,'F#1/Gb1':46.25,'G1':49.0,'G#1/Ab1':51.91,'A1':55.0,'A#1/Bb1':58.27,'B1':61.74,'C2':65.41,'C#2/Db2':69.3,'D2':73.42,'D#2/Eb2':77.78,'E2':82.41,'F2':87.31,'F#2/Gb2':92.5,'G2':98.0,'G#2/Ab2':103.83,'A2':110.0,'A#2/Bb2':116.54,'B2':123.47,'C3':130.81,'C#3/Db3':138.59,'D3':146.83,'D#3/Eb3':155.56,'E3':164.81,'F3':174.61,'F#3/Gb3':185.0,'G3':196.0,'G#3/Ab3':207.65,'A3':220.0,'A#3/Bb3':233.08,'B3':246.94,'C4':261.63,'C#4/Db4':277.18,'D4':293.66,'D#4/Eb4':311.13,'E4':329.63,'F4':349.23,'F#4/Gb4':369.99,'G4':392.0,'G#4/Ab4':415.3,'A4':440.0,'A#4/Bb4':466.16,'B4':493.88,'C5':523.25,'C#5/Db5':554.37,'D5':587.33,'D#5/Eb5':622.25,'E5':659.26,'F5':698.46,'F#5/Gb5':739.99,'G5':783.99,'G#5/Ab5':830.61,'A5':880.0,'A#5/Bb5':932.33,'B5':987.77,'C6':1046.5,'C#6/Db6':1108.73,'D6':1174.66,'D#6/Eb6':1244.51,'E6':1318.51,'F6':1396.91,'F#6/Gb6':1479.98,'G6':1567.98,'G#6/Ab6':1661.22,'A6':1760.0,'A#6/Bb6':1864.66,'B6':1975.53,'C7':2093.0,'C#7/Db7':2217.46,'D7':2349.32,'D#7/Eb7':2489.02,'E7':2637.02,'F7':2793.83,'F#7/Gb7':2959.96,'G7':3135.96,'G#7/Ab7':3322.44,'A7':3520.0,'A#7/Bb7':3729.31,'B7':3951.07,'C8':4186.01,'C#8/Db8':4434.92,'D8':4698.64,'D#8/Eb8':4978.03}

command = array.array('H', [6500, 0, 6500,
                            0])  # If the user wants to send the current command, without capturing a command previously in mode one, it will fail, this is a 'default' value

stealth = False  # Because this is reversed to due the button being connected to ground usually, if it is pressed it should enable stealth mode, causing a False value to enable stealth mode

freq = (700, 950,
        35)  # The frequencies to step between after sending the ir code. The tuple if the start value, the end value, and the amount to step between each time

wifi_possible = config['wifi_possible']
wifi_enabled = False


class Buttons:

    def __init__(self):
        self.wifi_en_current_value = False
        self.small_button_current_value = False
        self.large_button_current_value = False

    def wifi_en_val(self):
        if wifi_possible:
            event = wifi_en.events.get()
            if event:
                self.wifi_en_current_value = event.pressed
                return event.pressed
            else:
                return self.wifi_en_current_value
        else:
            return False

    def small_btn_val(self):
        event = small_button.events.get()
        if event:
            self.small_button_current_value = event.pressed
            return event.pressed
        else:
            return self.small_button_current_value

    def large_btn_val(self):
        event = large_button.events.get()
        if event:
            self.large_button_current_value = event.pressed
            return event.pressed
        else:
            return self.large_button_current_value


buttons = Buttons()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Functions Set Up

def realiser():
    """
       This is a super scary function that will alter your view of the world!
       Or rather it makes the program realise it's not always right.
    """

    print('Starting realiser')

    while buttons.large_btn_val() or buttons.small_btn_val():
        set_colour(white)
        time.sleep(0.1)
        set_colour(red)
        time.sleep(0.1)
        buttons.wifi_en_val()

    print('Realiser finished')

def set_colour(colour, button=True, neopixel=True):
    "This sets the colour of the button and neopixel based on a tuple in two lists"

    if button:
        r.duty_cycle = colour[0]
        g.duty_cycle = colour[1]
        b.duty_cycle = colour[2]

    if neopixel:
        pixel.fill(neo_colours[colours.index(colour)])

def tone(note: str, duration: int, speed=1, reinit=True):
    """
    This function plays a tone on the piezo
    """
    global piezo
    piezo.deinit()
    if note != "N":
        simpleio.tone(globals()[piezo_pin], int(round(notes[note], 0)), duration*speed)
    if reinit:
        piezo = pwmio.PWMOut(globals()[piezo_pin], variable_frequency=True)

def led_ir_indicate(current_command=None):
    """This blinks the led on and off the same way that the ir
    led would be blinked on and off when sending the infrared codes"""

    global led
    led.deinit()
    led = pulseio.PulseOut(globals()[config['led_pin']], duty_cycle=2 ** 15)
    if current_command == None:
        led.send(command)
    else:
        led.send(current_command)
    led.deinit()
    led = pwmio.PWMOut(globals()[config['led_pin']])


def rise_and_fall():
    """
    This just makes the pitch of the piezo go up and down, and the led fade in and out
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

def setup_mode():
    global mode
    global stealth
    global previous_mode
    global wifi_enabled

    if previous_mode != mode:
        print('Setup mode')
        previous_mode = mode

    set_colour(green)

    timer = time.monotonic()
    while time.monotonic() - timer < 3:
        if buttons.small_btn_val():
            stealth = True
        if buttons.wifi_en_val():
            wifi_enabled = True

    return


setup_mode()

if wifi_enabled:
    import wifi
    import socketpool
    import adafruit_requests
    import ssl

    set_colour(red)

    for network in wifi.radio.start_scanning_networks():
        print(network.ssid)
        for wnetwork in config['wifi_mode_config']['wifi_networks']:
            if wnetwork['ssid'] == network.ssid:
                print(f'Connecting to {wnetwork["ssid"]}')
                wifi.radio.connect(wnetwork['ssid'], wnetwork['password'], timeout=5000)
                wifi.radio.stop_scanning_networks()
                print("Wifi is connected to " + wnetwork['ssid'])

        if wifi.radio.connected:
            pool = socketpool.SocketPool(wifi.radio)
            time.sleep(1)
            requests = adafruit_requests.Session(pool, ssl.create_default_context())
            break

    if not wifi.radio.connected:
        wifi_enabled = False
        print('Could not connect to any of the configured wifi networks')

else:
    wifi_enabled = False


def dynamic_mode():
    """
    This mode can clone and send an ir remote codes to other ir devices
    """
    global mode
    global command
    global previous_mode

    if previous_mode != mode:
        print('Dynamic mode')
        previous_mode = mode
    set_colour(orange)

    if buttons.small_btn_val():
        set_colour(violet)
        ir_read.resume()

        while buttons.small_btn_val():
            time.sleep(0.01)
            if buttons.large_btn_val():
                ir_read.pause()
                ir_read.clear()

                while buttons.large_btn_val():
                    set_colour(white)
                    time.sleep(0.1)
                    set_colour(red)
                    time.sleep(0.1)

                mode += 1
                return

        time.sleep(0.1)  # The following fwe lines prevent accidental presses of the small button
        if buttons.small_btn_val():
            pass

        ir_read.pause()

        if len(ir_read) == 0:  # This block makes sure that the command variable is set properly, and not to None
            command = array.array('H', [6500, 0, 6500, 0])
        else:
            command = array.array('H', [ir_read[x] for x in range(len(ir_read))])
            led_ir_indicate()  # This flashes out the ir code using the main led, so the user knows an ir code has been captured

        print(f'Dynamic mode command captured is {command}')

        ir_read.clear()

    elif buttons.large_btn_val():
        ir_send.send(command)
        print(f'Dynamic mode command sent is {command}')

        if not stealth:
            vibrator.value = True
            piezo.duty_cycle = 60000

        while buttons.large_btn_val():
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

        time.sleep(0.1)


def annoying_mode():
    """
    This mode makes a high-pitched annoying tone so long as the button is being held down
    """

    global mode
    global previous_mode

    if previous_mode != mode:
        print('Annoying Mode')
        previous_mode = mode

    set_colour(red)

    if buttons.small_btn_val():
        while buttons.small_btn_val():
            if buttons.large_btn_val():
                while buttons.large_btn_val():
                    set_colour(white)
                    time.sleep(0.1)
                    set_colour(red)
                    time.sleep(0.1)
                mode += 1
                return

    elif buttons.large_btn_val():
        led.duty_cycle = 65535
        piezo.duty_cycle = 60000
        while buttons.large_btn_val():
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
    global previous_mode

    if previous_mode != mode:
        print('TV B Gone mode')
        previous_mode = mode

    set_colour(purple)

    while not buttons.large_btn_val():  # Wait until the large button is pressed before starting

        pass

    f = open("/codes.txt", "r")  # Read the list of codes
    for line in f:
        code = eval(line)
        print(f'TV B GONE mode code sent is {code}')
        if not stealth:  # If it's not stealth mode then flash the main led, piezo, and vibrator on and off
            led.duty_cycle = 65535
            vibrator.value = True
            piezo.duty_cycle = 60000
            rise_and_fall()
            vibrator.value = False
            led.duty_cycle = 0
            piezo.duty_cycle = 0

        else:  # Else, just flash the button's led
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

        if buttons.large_btn_val():  # If the large button was pressed, then switch to the next mode
            while buttons.large_btn_val():
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
    This mode has eight permanent storage banks, based on colour, that can hold one code per bank
    """

    global mode
    global previous_mode

    if previous_mode != mode:
        print('Permanent Bank Storage mode')
        previous_mode = mode

    bank = 0  # This is like the mode variable, but for only this function
    set_colour(aqua, neopixel=False)

    with open('bank.txt', 'r') as banks_txt:  # Open the banks.txt file, that holds the previously encoded values
        banks = banks_txt.readlines()
        if len(banks) < 7:  # If there is not 8 banks, then add banks
            while len(banks) < 8:  # Until there are 8 banks total
                banks.append(
                    '6500,0,6500,0')  # The pulses are stored as strings delimited by commas, for easy conversion to integers later

        for item in range(len(banks)):
            current_bank = banks[item].split(',')  # Split the string into a list based on the commas
            for string in range(
                    len(current_bank)):  # For each string, convert it to an integer, and save it as an integer in the same list
                current_bank[string] = int(current_bank[string])
            banks[item] = current_bank  # Add the converted bank to the program's banks variable

    while True:  # This is the final mode, and is insde it's own infinite loop
        set_colour(aqua, neopixel=False)
        break_up = False
        set_colour(colours[bank], button=False)
        if buttons.small_btn_val():  # Programming mode
            ir_read.clear()
            ir_read.resume()
            while buttons.small_btn_val():
                set_colour(violet, neopixel=False)
                if buttons.large_btn_val():  # To switch banks hold the small button and large button at the smae time
                    if not bank == 7:
                        bank += 1
                    else:
                        bank = 0
                    while buttons.large_btn_val():
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

            if [ir_read[x] for x in range(len(ir_read))] == []:  # Is ir_read empty?
                banks[bank] = [6500, 0, 6500, 0]  # If so, set it to a default value
            else:
                banks[bank] = [ir_read[x] for x in range(len(ir_read))]

            led_ir_indicate(
                array.array('H', banks[bank]))  # Use the main LED to show the user what was captured by the receiver

            with open('bank.txt',
                      'w') as banks_txt:  # Every time the ir receiver receives something, it is saved in the banks.txt file
                for item in banks:  # This loop converts the integers in the program's bamk variable to a stringed list that's comma delimited
                    code = ''
                    for pulse in item:
                        code += str(pulse) + ','
                    code = code[:-1]
                    if banks.index(item) == 7:
                        banks_txt.write(code)
                    banks_txt.flush()

        elif buttons.large_btn_val():
            ir_send.send(array.array('H', [int(banks[bank][x]) for x in range(len(banks[bank]))]))
            print(f'Sent {banks[bank]}')

            if not stealth:
                vibrator.value = True
                piezo.duty_cycle = 60000

            while buttons.large_btn_val():
                if not stealth:
                    rise_and_fall()
                else:
                    set_colour(black, neopixel=False)
                    time.sleep(0.3)
                    set_colour(red, neopixel=False)
                    time.sleep(0.3)
                    set_colour(aqua, neopixel=False)

            vibrator.value = False
            led.duty_cycle = 0
            piezo.duty_cycle = 0


def homeassistant_mode():
    global mode
    global previous_mode

    action = 0

    if previous_mode != mode:
        print('Home Assistant mode')
        previous_mode = mode

    set_colour(blue, neopixel=False)
    set_colour(colours[action], button=False)

    while action <= len(config['homeassistant_actions']) - 1:
        set_colour(blue, neopixel=False)
        if buttons.small_btn_val():
            while buttons.small_btn_val():
                if buttons.large_btn_val():
                    while buttons.large_btn_val():
                        set_colour(white)
                        time.sleep(0.1)
                        set_colour(red)
                        time.sleep(0.1)

                    if not action+1 >= len(config['homeassistant_actions']):
                        action += 1
                        set_colour(colours[action], button=False)
                    else:
                        return

        elif buttons.large_btn_val():
            print("Current action is: " + str(action))
            paction = config['homeassistant_actions'][action]

            headers = {"Authorization": f"Bearer {config['homeassistant_token']}"}

            if paction['entity_id'] != None:
                data = {"entity_id": paction['entity_id']}
                print(f'Sending POST request to HA: EID: {paction["entity_id"]} Service: {paction["service"]}')
            else:
                data = paction['custom_data']
                print(
                    f'Sending POST request to HA: Custom data: {paction["custom_data"]} Service: {paction["service"]}')

            if not stealth:
                vibrator.value = True
                piezo.duty_cycle = 60000
                rise_and_fall()

            harequest = requests.request('POST',
                                         f'{config["wifi_mode_config"]["homeassistant_url"]}/api/services/{paction["service"]}',
                                         json=data, headers=headers, stream=False)

            print('Finished sending request')
            print('Text response was ' + harequest.text)

            print("Stealth is: " + str(stealth))

            while buttons.large_btn_val():
                if not stealth:
                    vibrator.value = True
                    piezo.duty_cycle = 60000
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

def play_music():
    global mode
    global previous_mode
    set_colour(yellow)

    if previous_mode != mode:
        print('Music mode')
        previous_mode = mode

    if buttons.large_btn_val():
        if not stealth:
            try:
                song = config['song']
            except KeyError:
                print('No song specified, playing default song')
                song = config['default_song']
            for note in song:
                tone(note['note'], note['duration'], speed=1.1, reinit=False)
            tone('N', 0.001, reinit=True)
        else:
            set_colour(red, neopixel=False)
            time.sleep(1)
            set_colour(yellow)
    if buttons.small_btn_val():
        set_colour(violet)
        while buttons.small_btn_val():
            if buttons.large_btn_val():
                while buttons.large_btn_val():
                    set_colour(white)
                    time.sleep(0.1)
                    set_colour(red)
                    time.sleep(0.1)
                mode += 1

def send_ducky():
    global mode
    global previous_mode

    if previous_mode != mode:
        print('Ducky mode')
        previous_mode = mode

    set_colour(green)
    if buttons.large_btn_val():
        import ducky_interpreter as ducky
        with open('payload.txt') as file:
            lines = file.read().splitlines()
            for line in lines:
                if not buttons.small_btn_val():
                    if not stealth:
                        rise_and_fall()
                    ducky.process(line)
                else:
                    while buttons.small_btn_val():
                        set_colour(violet)
                        if buttons.large_btn_val():
                            while buttons.large_btn_val:
                                set_colour(white)
                                time.sleep(0.1)
                                set_colour(red)
                                time.sleep(0.1)
                            mode += 1
                            return

    if buttons.small_btn_val():
        while buttons.small_btn_val():
            set_colour(violet)
            if buttons.large_btn_val():
                while buttons.large_btn_val():
                    set_colour(white)
                    time.sleep(0.1)
                    set_colour(red)
                    time.sleep(0.1)
                mode += 1
                led.duty_cycle = 0
                return