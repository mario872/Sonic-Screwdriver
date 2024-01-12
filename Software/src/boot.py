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

import storage
import board
import digitalio
import microcontroller
import pwmio
import time

button = digitalio.DigitalInOut(board.GP6)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

r = pwmio.PWMOut(board.GP1)
#g = pwmio.PWMOut(board.GP2)
#b = pwmio.PWMOut(board.GP3)

r.duty_cycle = 65535
#g.duty_cylce = 65535
#b.duty_cylce = 65535

if not button.value:
    while not button.value:
        r.duty_cycle = 0
        time.sleep(0.1)
        r.duty_cycle = 65535
        time.sleep(0.1)
    
    microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER)
    microcontroller.reset()

storage.remount("/", False)