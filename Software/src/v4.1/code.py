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
import modes

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Main Loop

possible_modes = {"dynamic_mode": modes.dynamic_mode, "annoying_mode": modes.annoying_mode, "tv_b_gone_mode": modes.tv_b_gone_mode, "permanent_bank_storage_mode": modes.permanent_bank_storage_mode, "play_music": modes.play_music, "send_ducky": modes.send_ducky, "homeassistant_mode": modes.homeassistant_mode}
function_possible_modes = {}
for key in possible_modes.keys():
    function_possible_modes[possible_modes[key]] = key

if not modes.wifi_enabled:
    print('No Wifi, In Offline Mode')
    set_modes = []
    for a_mode in modes.config['offline_modes']:
        set_modes.append(possible_modes[a_mode])

else:
    print('Wifi Available, In Wifi Mode')
    set_modes = []
    for a_mode in modes.config['wifi_modes']:
        set_modes.append(possible_modes[a_mode])

print('Modes configured are:')
for p_mode in function_possible_modes:
    if p_mode in set_modes:
        print(' * ' + function_possible_modes[p_mode])

modes.realiser()

print('Entering main loop')

while True:
    set_modes[modes.mode]()  # Execute a function in the modes list based on the current mode
