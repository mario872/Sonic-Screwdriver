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

led = pwmio.PWMOut(board.GP14, frequency=5000, duty_cycle=0)

piezo = pwmio.PWMOut(board.GP8, frequency=1000, duty_cycle=0)

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

def rainbowLED():
    resetRGBLEDValues()
    timeLength = 0.0009
    for i in range(0, 2000):
        redLed.duty_cycle = i
        time.sleep(timeLength)
    for i in range(0, 2000):
        greenLed.duty_cycle = i
        time.sleep(timeLength)
    for i in reversed(range(0, 2000)):
        redLed.duty_cycle = i
        time.sleep(timeLength)
    for i in range(0, 2000):
        blueLed.duty_cycle = i
        time.sleep(timeLength)
    for i in reversed(range(0, 2000)):
        greenLed.duty_cycle = i
        time.sleep(timeLength)
    for i in range(0, 2000):
        redLed.duty_cycle = i
        time.sleep(timeLength)
    for i in reversed(range(0, 2000)):
        redLed.duty_cycle = i
        blueLed.duty_cycle = i
        time.sleep(timeLength)
#0 = Normal: IR, random tones etc. Color = Orange/Yellow
#1 = Sustained Annoying Tones. Color = Red
#2 = Pretend Pairing Mode: Fading Light, Fading Piezo etc. Color = Green Fade

# mode = -1
ir_read.pause()

mode = 2
maxModePlus1 = 5
resetRGBLEDValues()
loop = 1

i = 0

command = array.array('H', [65000, 100, 65000, 100])

while True:
#     if not smallButton.value:
#         if mode + 1 != maxModePlus1:
#             mode += 1
#         else:
#             mode = 0
#         print(str(mode))
    if mode == 0:
        if loop != 1:
            redLed.duty_cycle = 20000
            greenLed.duty_cycle = 5000
        elif loop == 1:
#             rainbowLED()
#             time.sleep(2)
            for i in range(0, 20000):
                if i < 5001:
                    greenLed.duty_cycle = i
                redLed.duty_cycle = i
                time.sleep(.000000000001)
            loop = 2
        else:
            resetRGBLEDValues()
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
        
    if mode == 1:
        resetRGBLEDValues()
        redLed.duty_cycle = 10000
        if not largeButton.value:
            #IR Stuff happens here
            resetRGBLEDValues()
            while not largeButton.value:
                led.duty_cycle = 65535
                piezo.duty_cycle = 60000
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
    #print("Above mdeo two a weiner lies, catch that weiner catch the skies " + str(i))
    #i = i+1
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
                if not largeButton.value:
                    time.sleep(.5)
                    if not  largeButton.value:
                        mode = 3
                        led.deinit()
                        led = pwmio.PWMOut(board.GP14, frequency=5000, duty_cycle=0)
                        pulse.deinit()
                        ir_led = pulseio.PulseOut(board.GP13, frequency=38000, duty_cycle=2**15)
                        time.sleep(.5)
                        breakI = True
                        print(str(breakI))
                        while not largeButton.value:
                            led.duty_cycle = random.randint(100, 65535)
                            piezo.duty_cycle = random.randint(100, 65535)
                        led.duty_cycle = 0
                        piezo.duty_cycle = 0
                            
            f.close()
        i += 1
        
#################################################################################################################
        
    if mode == 3:
        resetRGBLEDValues()
        blueLed.duty_cycle =  2000
        redLed.duty_cycle = 2000
        greenLed.duty_cycle = 2000
        led.deinit()
        led = DigitalInOut(board.GP14)
        led.direction = Direction.OUTPUT
        breakI = False
        #print("Yahpppppp" + str(i) + str(largeButton.value))
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
                if largeButton.value:
                    mode = 4
                    time.sleep(.5)
                    breakI = True
                    print(str(breakI))
                    while not largeButton.value:
                        led.duty_cycle = random.randint(100, 65535)
                        piezo.duty_cycle = random.randint(100, 65535)
                    led.duty_cycle = 0
                    piezo.duty_cycle = 0
            led.duty_cycle = 0
            piezo.duty_cycle = 0
            time.sleep(1)
        time.sleep(.5)        
        
###########################################################################################################
#     if mode == 4:
#         #print("Here at mode 3")
#         resetRGBLEDValues()
#         blueLed.duty_cycle = 2000
#         if not largeButton.value:
#             print("Button was pressed")
#             ir_led.send(array.array('H', [9087, 4450, 603, 557, 575, 558, 574, 559, 573, 560, 572, 561, 572, 560, 572, 561, 571, 562, 602, 1635, 608, 1658, 607, 1659, 605, 1660, 604, 1662, 602, 1663, 602, 1664, 600, 1665, 600, 560, 603, 531, 601, 532, 601, 531, 601, 532, 600, 533, 599, 1639, 636, 524, 608, 1630, 635, 1631, 633, 1632, 633, 1633, 631, 1635, 629, 1637, 628, 532, 600, 1638, 637, 39728, 9078, 2221, 631, 65535, 9081, 2210, 600]))
#             while not largeButton.value:
#                 #print("In button Loop")
#                 resetRGBLEDValues()
#                 led.duty_cycle = random.randint(100, 65535)
#                 piezo.duty_cycle = random.randint(100, 65535)
#             led.duty_cycle = 0
#             piezo.duty_cycle = 0
#             blueLed.duty_cycle = 2000
#         if smallButton.value:
#             time.sleep(.25)
#             if not largeButton.value:
#                 mode = 4
#                 break
###########################################################################################################                
                
    if mode == 4:
        resetRGBLEDValues()
        for i in range(0, 20000):
            greenLed.duty_cycle = i
            piezo.duty_cycle = i*3
            while smallButton.value:
                if not largeButton.value:
                    if mode + 1 != maxModePlus1:
                        mode += 1
                    else:
                        mode = 0
                    print(str(mode))
                    while not largeButton.value:
                        time.sleep(.25)
        time.sleep(.0005)
        print("Finished Up")
        for i in range(20000, 0, -1):
            greenLed.duty_cycle = i
            piezo.duty_cycle = i*3
            while smallButton.value:
                if not largeButton.value:
                    if mode + 1 != maxModePlus1:
                        mode += 1
                    else:
                        mode = 0
                    print(str(mode))
                    while not largeButton.value:
                        time.sleep(.25)
            time.sleep(.0005)
            
        print("Finished Down")
        
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
