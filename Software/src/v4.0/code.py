import time
import board
from digitalio import DigitalInOut, Direction, Pull
import pwmio
import digitalio
import random
import alarm
import pulseio
import array

#Order of apple remote capture
#1. MENU
#2. PAUSE
#3. UP
#4. DOWN
#5. LEFT
#6. RIGHT
#7. SELECT

debug = False

piezo = True

led = pwmio.PWMOut(board.GP14, frequency=5000, duty_cycle=0)

if piezo:
    piezo = pwmio.PWMOut(board.GP8, frequency=1000, duty_cycle=0)
else:
    piezo = pwmio.PWMOut(board.GP2, frequency=1000, duty_cycle=0)

redLed = pwmio.PWMOut(board.GP6, frequency=5000, duty_cycle=0)
greenLed = pwmio.PWMOut(board.GP4, frequency=5000, duty_cycle=0)
blueLed = pwmio.PWMOut(board.GP5, frequency=5000, duty_cycle=0)

ir_read = pulseio.PulseIn(board.GP18, maxlen=100, idle_state=True)
ir_led = pulseio.PulseOut(board.GP13, frequency=38000, duty_cycle=2**15)

largeButton = DigitalInOut(board.GP9)
largeButton.direction = Direction.INPUT
largeButton.pull = Pull.UP

smallButton = digitalio.DigitalInOut(board.GP1)
smallButton.direction = digitalio.Direction.INPUT
smallButton.pull = digitalio.Pull.UP

#pulses = []

def resetRGBLEDValues():
    redLed.duty_cycle = 0
    greenLed.duty_cycle = 0
    blueLed.duty_cycle = 0

def rainbowLED(timeLength=0.0009, stop=None, valuer=True):
    resetRGBLEDValues()
    for i in range(0, 2000):
        redLed.duty_cycle = i
        time.sleep(timeLength)
        if stop != None:
            if stop.value == valuer:
                return
    for i in range(0, 2000):
        greenLed.duty_cycle = i
        time.sleep(timeLength)
        if stop != None:
            if stop.value == valuer:
                return
    for i in reversed(range(0, 2000)):
        redLed.duty_cycle = i
        time.sleep(timeLength)
        if stop != None:
            if stop.value == valuer:
                return
    for i in range(0, 2000):
        blueLed.duty_cycle = i
        time.sleep(timeLength)
        if stop != None:
            if stop.value == valuer:
                return
    for i in reversed(range(0, 2000)):
        greenLed.duty_cycle = i
        time.sleep(timeLength)
        if stop != None:
            if stop.value == valuer:
                return
    for i in range(0, 2000):
        redLed.duty_cycle = i
        time.sleep(timeLength)
        if stop != None:
            if stop.value == valuer:
                return
    for i in reversed(range(0, 2000)):
        redLed.duty_cycle = i
        blueLed.duty_cycle = i
        time.sleep(timeLength)
        if stop != None:
            if stop.value == valuer:
                return

# mode = -1
ir_read.pause()

mode = 0
maxModePlus1 = 4
resetRGBLEDValues()

i = 0

# for i in range(0, 20000):
#     if i < 5001:
#         greenLed.duty_cycle = i
#     redLed.duty_cycle = i
#     time.sleep(.000000000001)

rainbowLED(timeLength=0.0006, stop=largeButton, valuer=False)

command = array.array('H', [65000, 100, 65000, 100])

while True:
    if debug:
        print(str(mode))
            
#########################################################################################################
    #Mode 0 - Normal: IR, random tones etc. Colour = Orange/Yellow
    if mode == 0:
        redLed.duty_cycle = 20000
        greenLed.duty_cycle = 5000
        
        while smallButton.value:
            if smallButton.value:
                print("Clearing IR")
                ir_read.clear()
                ir_read.resume()
                while smallButton.value:
                    if not largeButton.value:
                        if mode + 1 != maxModePlus1:
                            mode += 1
                        else:
                            mode = 0
                        print(str(mode))
                        while not largeButton.value:
                            time.sleep(.25)
                    
                ir_read.pause()
                command = array.array('H', [ir_read[x] for x in range(len(ir_read))])
                led.deinit()
                led = pulseio.PulseOut(board.GP14, frequency=38000, duty_cycle=2**15)
                led.send(command)
                led.deinit()
                led = pwmio.PWMOut(board.GP14, frequency=5000, duty_cycle=0)
                print("Finished reading ir and compiled")
                print(str(command))
                #pulses.append(command)
                
        if not largeButton.value:
            print('IR COMMAND IS: ' + str(command))
            time.sleep(.5)
            while largeButton.value:
                led.duty_cycle = 65535
            resetRGBLEDValues()
            for c in range(1, 5000):
                led.duty_cycle = random.randint(100, 65535)
                piezo.duty_cycle = random.randint(100, 65535)
            print("Finished pre-dance")
            #for com in pulses:
            ir_led.send(command)
                #print(str(com))
                #time.sleep(.25)
            print("Sent IR")
            while not largeButton.value:
                led.duty_cycle = random.randint(100, 65535)
                piezo.duty_cycle = random.randint(100, 65535)
            led.duty_cycle = 0
            piezo.duty_cycle = 0
                
        else:
            continue
        
#########################################################################################################
    #Mode 1: Sustained Annoying Tones. Color = Red
    if mode == 1:
        resetRGBLEDValues()
        redLed.duty_cycle = 10000
        if not largeButton.value:
            #IR Stuff happens here
            resetRGBLEDValues()
            while not largeButton.value:
                led.duty_cycle = 65535
                piezo.duty_cycle = 65535
                if smallButton.value:
                    if mode + 1 != maxModePlus1:
                        mode += 1
                    else:
                        mode = 0
                    print(str(mode))
                    while smallButton.value:
                        time.sleep(.25)
                continue
            led.duty_cycle = 0
            piezo.duty_cycle = 0
        else:
            continue
        
#########################################################################################################
    #Mode 2: BLAST IR EVERYWHERE! - Purple: Tries evveery on/off code that it knows to try and turn off any tv
    if mode == 2:
        resetRGBLEDValues()
        blueLed.duty_cycle =  2000
        redLed.duty_cycle = 2000
        led.deinit()
        led = DigitalInOut(board.GP14)
        led.direction = Direction.OUTPUT
        breakI = False
        #print("Yahpppppp" + str(i) + str(largeButton.value))
        while not largeButton.value:
            f = open("/codes.txt", "r")
            time.sleep(.5)
            for line in f:
                if breakI == True:
                    print(str(breakI))
                    break 
                code = eval(line)
                print(code)
                led.value = True
                # If this is a repeating code, extract details
                try:
                    repeat = code["repeat"]
                    delay = code["repeat_delay"]
                except KeyError:  # by default, repeat once only!
                    repeat = 1
                    delay = 0
                # The table holds the on/off pairs
                table = code["table"]
                pulses = []  # store the pulses here
                # Read through each indexed element
                for i in code["index"]:
                    pulses += table[i]  # and add to the list of pulses
                pulses.pop()  # remove one final 'low' pulse
                ir_led.deinit()
                with pulseio.PulseOut(
                    board.GP13, frequency=code["freq"], duty_cycle=2**15
                ) as pulse:
                    for i in range(repeat):
                        pulse.send(array.array("H", pulses))
                        time.sleep(delay)

                led.value = False
                time.sleep(code["delay"])
                if smallButton.value:
                    mode = 3
                    led.deinit()
                    led = pwmio.PWMOut(board.GP14, frequency=5000, duty_cycle=0)
                    pulse.deinit()
                    ir_led = pulseio.PulseOut(board.GP13, frequency=38000, duty_cycle=2**15)
                    time.sleep(.5)
                    breakI = True
                    print(str(breakI))
            f.close()
        i += 1
        
#################################################################################################################
    #Mode 3 - Epson Whiteboards: I think that this mode turns on and off Epson whiteboards - Purple I think?
    if mode == 3:
        resetRGBLEDValues()
        blueLed.duty_cycle =  2000
        #redLed.duty_cycle = 2000
        #greenLed.duty_cycle = 2000
        led.deinit()
        led = DigitalInOut(board.GP14)
        led.direction = Direction.OUTPUT
        breakI = False
        
        while not largeButton.value:
            led.deinit()
            led = DigitalInOut(board.GP14)
            led.direction = Direction.OUTPUT
            if breakI == True:
                break
            f = open("/remote.txt", "r")
            time.sleep(.1)
            for line in f:
                if breakI == True:
                    print(str(breakI))
                    break 
                code = eval(line)
                print(code)
                led.value = True
                # If this is a repeating code, extract details
                try:
                    repeat = code["repeat"]
                    delay = code["repeat_delay"]
                except KeyError:  # by default, repeat once only!
                    repeat = 1
                    delay = 0
                # The table holds the on/off pairs
                table = code["table"]
                pulses = []  # store the pulses here
                # Read through each indexed element
                for i in code["index"]:
                    pulses += table[i]  # and add to the list of pulses
                pulses.pop()  # remove one final 'low' pulse
                ir_led.deinit()
                with pulseio.PulseOut(
                    board.GP13, frequency=code["freq"], duty_cycle=2**15
                ) as pulse:
                    for i in range(repeat):
                        pulse.send(array.array("H", pulses))
                        time.sleep(delay)

                led.value = False
                time.sleep(code["delay"])
            f.close()
            led.deinit()
            led = pwmio.PWMOut(board.GP14, frequency=5000, duty_cycle=0)
            pulse.deinit()
            ir_led = pulseio.PulseOut(board.GP13, frequency=38000, duty_cycle=2**15)
            while not largeButton.value:
                led.duty_cycle = random.randint(100, 65535)
                piezo.duty_cycle = random.randint(100, 65535)
                if smallButton.value:
                    mode = 4
                    time.sleep(.5)
                    breakI = True
                    print(str(breakI))
            led.duty_cycle = 0
            piezo.duty_cycle = 0
            time.sleep(1)
        time.sleep(.5)
        
###########################################################################################################
    #Mode 4 - Pretend Pairing: I have no idea why this is still in the code,
    #but whatever, Green fading LED and fading and rising piezo
#     if mode == 4:
#         resetRGBLEDValues()
#         for i in range(0, 20000):
#             greenLed.duty_cycle = i
#             piezo.duty_cycle = i*3
#             while smallButton.value:
#                 if not largeButton.value:
#                     if mode + 1 != maxModePlus1:
#                         mode += 1
#                     else:
#                         mode = 0
#                     print(str(mode))
#                     while not largeButton.value:
#                         time.sleep(.25)
#         time.sleep(.0005)
#         print("Finished Up")
#         for i in range(20000, 0, -1):
#             greenLed.duty_cycle = i
#             piezo.duty_cycle = i*3
#             while smallButton.value:
#                 if not largeButton.value:
#                     if mode + 1 != maxModePlus1:
#                         mode += 1
#                     else:
#                         mode = 0
#                     print(str(mode))
#                     while not largeButton.value:
#                         time.sleep(.25)
#             time.sleep(.0005)
#             
#         print("Finished Down")
#         
        #Secret last mode for deep sleep
#     if mode == 6:
#         resetRGBLEDValues()
#         blueLed.duty_cycle = 10000
#         time.sleep(1)
#         resetRGBLEDValues()
#         largeButton.deinit()
#         pin_alarm = alarm.pin.PinAlarm(pin=board.GP9, value=False, pull=True)
# 
#         # Exit the program, and then deep sleep until the alarm wakes us.
#         resetRGBLEDValues()
#         alarm.exit_and_deep_sleep_until_alarms(pin_alarm)
