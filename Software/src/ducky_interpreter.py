"""
The original code here is under the MIT licence, and was written by ShayBox on GitHub
This original link to this code (hopefully) is available at https://github.com/ShayBox/CircuitPython-DuckyScript
This code has been modified to work as a library for this device
"""

import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)

default_delay = 0
previous_line = ''

def press(k):
    keys = {
        keys = {
        'ENTER': Keycode.ENTER,
        'RETURN': Keycode.ENTER,  # Added alternative for ENTER
        'ESC': Keycode.ESCAPE,
        'ESCAPE': Keycode.ESCAPE,  # Added alternative for ESCAPE
        'BACKSPACE': Keycode.BACKSPACE,
        'TAB': Keycode.TAB,
        'SPACE': Keycode.SPACEBAR,
        'SPACEBAR': Keycode.SPACEBAR,  # Added alternative for SPACE
        'MINUS': Keycode.MINUS,
        'EQUAL': Keycode.EQUALS,
        'EQUALS': Keycode.EQUALS,  # Added alternative for EQUALS
        'LEFT_BRACKET': Keycode.LEFT_BRACKET,
        'LEFTBRACKET': Keycode.LEFT_BRACKET,  # Added alternative for LEFT_BRACKET
        'RIGHT_BRACKET': Keycode.RIGHT_BRACKET,
        'RIGHTBRACKET': Keycode.RIGHT_BRACKET,  # Added alternative for RIGHT_BRACKET
        'BACKSLASH': Keycode.BACKSLASH,
        'POUND': Keycode.POUND,
        'SEMICOLON': Keycode.SEMICOLON,
        'QUOTE': Keycode.QUOTE,
        'TILDE': Keycode.GRAVE_ACCENT,
        'COMMA': Keycode.COMMA,
        'PERIOD': Keycode.PERIOD,
        'SLASH': Keycode.FORWARD_SLASH,
        'FORWARD_SLASH': Keycode.FORWARD_SLASH,  # Added alternative for FORWARD_SLASH
        'FORWARDSLASH': Keycode.FORWARD_SLASH,  # Added alternative for FORWARDSLASH
        'CAPS': Keycode.CAPS_LOCK,
        'CAPS_LOCK': Keycode.CAPS_LOCK,  # Added alternative for CAPS_LOCK
        'PRINT': Keycode.PRINT_SCREEN,
        'PRINT_SCREEN': Keycode.PRINT_SCREEN,  # Added alternative for PRINT_SCREEN
        'SCROLL': Keycode.SCROLL_LOCK,
        'SCROLL_LOCK': Keycode.SCROLL_LOCK,  # Added alternative for SCROLL_LOCK
        'PAUSE': Keycode.PAUSE,
        'BREAK': Keycode.PAUSE,  # Added alternative for BREAK
        'INSERT': Keycode.INSERT,
        'HOME': Keycode.HOME,
        'PAGE_UP': Keycode.PAGE_UP,
        'PAGEUP': Keycode.PAGE_UP,  # Added alternative for PAGEUP
        'DELETE': Keycode.DELETE,
        'END': Keycode.END,
        'PAGE_DOWN': Keycode.PAGE_DOWN,
        'PAGEDOWN': Keycode.PAGE_DOWN,  # Added alternative for PAGEDOWN
        'RIGHT': Keycode.RIGHT_ARROW,
        'RIGHT_ARROW': Keycode.RIGHT_ARROW,  # Added alternative for RIGHT_ARROW
        'LEFT': Keycode.LEFT_ARROW,
        'LEFT_ARROW': Keycode.LEFT_ARROW,  # Added alternative for LEFT_ARROW
        'DOWN': Keycode.DOWN_ARROW,
        'DOWN_ARROW': Keycode.DOWN_ARROW,  # Added alternative for DOWN_ARROW
        'UP': Keycode.UP_ARROW,
        'UP_ARROW': Keycode.UP_ARROW,  # Added alternative for UP_ARROW
        'NUM': Keycode.NUM_LOCK,
        'NUM_LOCK': Keycode.NUM_LOCK,  # Added alternative for NUM_LOCK
        'APPLICATION': Keycode.APPLICATION,
        'MENU': Keycode.APPLICATION,  # Added alternative for MENU
        'LEFT_CONTROL': Keycode.LEFT_CONTROL,
        'CONTROL': Keycode.LEFT_CONTROL,  # Added alternative for CONTROL
        'CTRL': Keycode.LEFT_CONTROL,  # Added alternative for CTRL
        'LEFT_SHIFT': Keycode.LEFT_SHIFT,
        'SHIFT': Keycode.LEFT_SHIFT,  # Added alternative for SHIFT
        'LEFT_GUI': Keycode.LEFT_GUI,
        'GUI': Keycode.LEFT_GUI,  # Added alternative for GUI
        'LEFT_WINDOWS': Keycode.LEFT_WINDOWS,
        'WINDOWS': Keycode.LEFT_WINDOWS,  # Added alternative for WINDOWS
        'RIGHT_CONTROL': Keycode.RIGHT_CONTROL,
        'RIGHT_SHIFT': Keycode.RIGHT_SHIFT,
        'RIGHT_ALT': Keycode.RIGHT_ALT,
        'RIGHT_GUI': Keycode.RIGHT_GUI,
        'F1': Keycode.F1,
        'F2': Keycode.F2,
        'F3': Keycode.F3,
        'F4': Keycode.F4,
        'F5': Keycode.F5,
        'F6': Keycode.F6,
        'F7': Keycode.F7,
        'F8': Keycode.F8,
        

    }

    if len(k) == 1:
        layout.write(k[0])

    for
    elif k == 'F19':
        kbd.press(Keycode.F19)

def process(line):
    args = line.split(' ', 1)
    inst = args[0]

    if inst == 'REM':
        return

    global default_delay
    global previous_line

    if default_delay > 0:
        time.sleep(default_delay / 1000)

    if inst == 'DEFAULT_DELAY' or inst == 'DEFAULTDELAY':
        try:
            default_delay = int(args[1])
        except ValueError:
            return
    elif inst == 'DELAY':
        try:
            time.sleep(int(args[1]) / 1000)
        except ValueError:
            return
    elif inst == 'STRING_DELAY' or inst == 'STRINGDELAY':
        try:
            args_1 = args[1].split(' ', 1)
            for c in args_1[1]:
                layout.write(c)
                time.sleep(int(args_1[0]) / 1000)
        except ValueError:
            return
    elif inst == 'STRING':
        layout.write(args[1])
    elif inst == 'REPEAT':
        try:
            for _ in range(int(args[1])):
                process(previous_line)
        except ValueError:
            return
    else:
        press(inst)
        if len(args) > 1:
            for s in args[1].split(' '):
                press(s)

    previous_line = line

    kbd.release_all()