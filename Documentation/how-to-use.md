# How to Use the Sonic Screwdriver 4.3
# Modes
The Sonic Screwdriver 4.3 has multiple modes, that can be used to accomplish different functions.
By default, the Sonic Screwdriver has 4 modes enabled + wifi mode.
The four offline modes are:
1. Dynamic Mode - Orange
 * Uses the Infrared Receiver to clone codes from remote controls once, and will not be remembered once the Sonic Screwdriver is off.
 * Sends cloned code to a tv or other device
2. TV B Gone Mode - Purple
 * Uses codes harvested by [Adafruit]('https://adafruit.com') from the TV B Gone to guess which codes will turn off a tv
 * There are around 200 codes, which can take up to 3 minutes to send all of
3. Annoying Mode - Red
 * Just an annoying high pitched buzzing sound
4. Permanent Storage Mode - Aqua
 * 7/8 different codes can be stored, even after reboots, and can be sent to tvs
 * Uses the infrared receiver to capture codes from remote controls

These modes can be changed in the config.json file.

There is also wifi mode, which when you press the wifi enable button when the lights turn green, will cause the Sonic Screwdriver to try and connect to the first wifi network it can on a list of wifi networks you can configure in config.json.
Wifi mode, currently only has one mode written for it, but I encourage you to create your own modes if you can.
The only currently written mode is home assistant mode, which can (theoretically) trigger any device/service/automation that the home assistant api can.

## How to Switch Between Modes
The first mode you are presented with upon first boot of your Sonic Screwdriver is setup mode, which you can identify by it's green colour.
If you press the wifi button while the Sonic Screwdriver is green, then wifi mode will be acctivated.
If you press the back button while it is green, then stealth will be turned on.
Stealth will turn off noise and vibrations on the Sonic Screwdriver until you turn it off.
You can press both the wifi button and back button to activate both stealth and wifi mode at the same time.

If you chose to press the wifi button, proceed to step 7(?)

### Step 1 - Dynamic Mode
To clone a remote, press and hold the back button, the Sonic Screwdriver will turn violet, continue holding the back button, while you aim your chosen remote at the front of the Sonic Screwdriver, then press the button you want to clone on the remote.
You should then be able to let go of the back button.
Immeadietely after unpressing the back button, the front LED should flash on and off very fast for around half a second.
This means the code was successfully captured.
To send the code press the large button on the Sonic Screwdriver. If you choose to hold it down, it should buzz and make a warbling noise.
It takes less than half a second to send the code, so don't feel you have to keep on holding it down.

### Step 2 - Changing Modes
While this is not a mode in itself, it does deserve it's own step.
This applies any time you want to switch between modes.
To go forward one mode, press and hold the back button. While still holding the back button, press the large button until the large button starts flashing red. Release both buttons and the colour should change ot the colour of the next mode.

### Step 3 - TV Hijacking Mode
TV Hijacking mode is given a list of around 250 common codes that are used to turn off tvs.
This list was gathered by Adafruit Industries, and kindly listed for free [here](https://learn.adafruit.com/circuitpython-tv-zapper-with-circuit-playground-express/)
