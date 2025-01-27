import adafruit_dht
import adafruit_apds9960.apds9960
import adafruit_apds9960.colorutility
import adafruit_icm20x
import pulseio
from rainbowio import colorwheel
import array
import time
import math # Not math, that's disgusting
import json
import gc
import adafruit_max1704x
import pwmio

gc.enable()
gc.collect()

config = json.load(open('config.json', 'r'))

def update_menu(menu, text):
    new_text = ""
    menu_list = []
    for i in range(menu.get_current_index(), menu.get_current_index()+4):
        menu_list.append(menu.get_current_menu()['items'][i % len(menu.get_current_menu()['items'])])
    for item in menu_list:
        if menu.is_current_item(item):
            new_text += ('* ' + item['title'] + '\n')
        else:
            new_text += (item['title'] + '\n')
            
    text.text = new_text

def update_position_and_menu(menu, text, select_button, l_btn, r_btn):
    changed_pos = False       
    if not select_button.value:
        t = time.monotonic_ns()/1000000000
        while not select_button.value:
            pass
        if time.monotonic_ns()/1000000000 - t < 0.75:
            gc.collect()
            changed_pos = True
            menu.inward()
        else:
            changed_pos = True
            menu.outward()
        update_menu(menu, text)
    
    if not r_btn.value:
        changed_pos = True
        menu.forward()
        time.sleep(0.1)
    if not l_btn.value:
        changed_pos = True
        menu.backward()
        time.sleep(0.1)
        
    if changed_pos:
        update_menu(menu, text)

class DHT22:
    def __init__(self, pin):
        self.old_temp = None
        self.old_humidity = None
        self.sensor = adafruit_dht.DHT22(pin)
        
    def temperature(self):
        try:
            temp = self.sensor.temperature
            self.old_temp = temp
            return temp
        except RuntimeError:
            return self.old_temp
        
    def humidity(self):
        try:
            humidity = self.sensor.humidity
            self.old_humidity = humidity
            return humidity
        except RuntimeError:
            return self.old_humidity
        
    def display_temp_humidity(self, text, btn, btn_pressed_val=False):
        while btn.value == btn_pressed_val:
            pass
        
        time.sleep(0.1)
        while not btn.value == btn_pressed_val:
            text.text = f"Temp: {str(self.temperature())}°C\nHumidity: {str(self.humidity())}%"
            
        while btn.value == btn_pressed_val:
            pass

class APDS9600:
    def __init__(self, i2c):
        self.sensor = adafruit_apds9960.apds9960.APDS9960(i2c)
        self.sensor.enable_proximity = False
        self.sensor.enable_gesture = False
        self.sensor.enable_color = False
        self.sensor.enable_proximity_interrupt = False
        
    def display_colour(self, text, btn, btn_pressed_val=False):
        while btn.value == btn_pressed_val:
            pass
        
        self.sensor.enable_color = True
        
        time.sleep(0.1)
        while not btn.value == btn_pressed_val:
            r, g, b, c = self.sensor.color_data
            text.text = f"Red: {str(int(round(r/65535*100, 0)))}%\nGreen: {str(int(round(g/65535*100, 0)))}%\nBlue: {str(int(round(b/65535*100, 0)))}%\nLux: {str(adafruit_apds9960.colorutility.calculate_lux(r, g, b))}"
            
        while btn.value == btn_pressed_val:
            pass
        
        self.sensor.enable_color = False
        
    def display_proximity(self, text, btn, btn_pressed_val=False):
        while btn.value == btn_pressed_val:
            pass
        
        self.sensor.enable_proximity = True
        
        time.sleep(0.1)
        while not btn.value == btn_pressed_val:
            proximity = self.sensor.proximity
            text.text = f"Proximity: {str(proximity)}\n\nNo units available.\nMax value is 255"
            
        while btn.value == btn_pressed_val:
            pass
        
        self.sensor.enable_proximity = False
        
class ICM20948:
    def __init__(self, i2c):
        self.sensor = adafruit_icm20x.ICM20948(i2c)
    
    def display_gyro(self, text, btn, btn_pressed_val=False):
        # I don't need to understand how this works because of AI
        alpha = 0.98
        pitch = 0.0
        roll = 0.0
        gyro_pitch = 0.0
        gyro_roll = 0.0
        
        while btn.value == btn_pressed_val:
            pass
        
        time.sleep(0.1)
        previous_time = time.time()
        while not btn.value == btn_pressed_val:
            current_time = time.time()
            dt = current_time - previous_time
            previous_time = current_time
            
            gyro = self.sensor.gyro
            accel = self.sensor.acceleration
            
             # Calculate pitch and roll from accelerometer data
            accel_pitch = math.atan2(accel[0], accel[2]) * 180 / math.pi
            accel_roll = math.atan2(accel[1], accel[2]) * 180 / math.pi
            
            # Calculate pitch and roll from gyroscope data (integrate angular velocity)
            gyro_pitch += gyro[1] * dt  # dt is the time interval between readings
            gyro_roll += gyro[0] * dt
            
            pitch = alpha * gyro_pitch + (1 - alpha) * accel_pitch
            roll = alpha * gyro_roll + (1 - alpha) * accel_roll
            
            text.text = f"Pitch: {str(round(pitch, 2))}°\nRoll: {str(round(roll, 2))}°"
            
        while btn.value == btn_pressed_val:
            pass
        
    def display_compass(self, text, btn, btn_pressed_val=False):
        while btn.value == btn_pressed_val:
            pass
        
        time.sleep(0.1)
        while not btn.value == btn_pressed_val:
            mag = self.sensor.magnetic
            heading = math.atan2(mag[1], mag[0])
            heading_degrees = heading * 180 / math.pi
            if heading_degrees < 0:
                heading_degrees += 360
            
            text.text = f"Heading: {str(round(heading_degrees, 2))}°"
            
        while btn.value == btn_pressed_val:
            pass
        
class IRSENDER:
    def __init__(self, pin, frequency: int = 38000, duty_cycle: int = 2**15):
        self.sender = pulseio.PulseOut(pin, frequency=frequency, duty_cycle=duty_cycle)
        self.sender_pin = pin
        self.sender_frequency = frequency
        self.sender_duty_cycle = duty_cycle
    
    def send_signal(self, signal: array, btn, btn_pressed_val, display_neopixel: bool = False, chosen_neopixel=None):
        while btn.value == btn_pressed_val:
            pass
        
        if signal != []:
            self.sender.send(signal)
            if display_neopixel:
                i = 0
                while i < len(signal):
                    if display_neopixel:
                        try:
                            chosen_neopixel.fill(colorwheel(i%255))
                            time.sleep(signal[i]/1000000)
                            i += 1
                            chosen_neopixel.fill((0, 0, 0))
                            time.sleep(signal[i]/1000000)
                            i+=1
                        except IndexError:
                            chosen_neopixel.fill((0, 0, 0))
                    else:
                        pass
        else:
            if display_neopixel:
                for i in range(2):
                    chosen_neopixel.fill((255, 0, 0))
                    time.sleep(0.3)
                    chosen_neopixel.fill((0, 0, 0))
                    time.sleep(0.3)
            else:
                pass
              
    def tv_b_gone(self, text, btn, btn_pressed_val=False, display_neopixel=True, chosen_neopixel=None):
        while btn.value == btn_pressed_val:
            pass
        
        f = open("/codes.txt", "r")
        count = 0
        for line in f:
            code = eval(line)
            text.text = f"Sending:\n{str(code['index'])[0:20]}"
            if display_neopixel:
                chosen_neopixel.fill((0, 0, 0))
                chosen_neopixel[count % 7] = (0, 0, 255)
            else:
                pass
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

            self.sender.deinit()
            with pulseio.PulseOut(
                self.sender_pin, frequency=code["freq"], duty_cycle=2**15
            ) as pulse:
                for i in range(repeat):
                    pulse.send(array.array("H", pulses))
                    time.sleep(delay)

            if display_neopixel:
                chosen_neopixel.fill((0, 0, 0))
                
            if btn.value == btn_pressed_val:
                break

            time.sleep(code["delay"])
            count += 1

        f.close()
            
        while btn.value == btn_pressed_val:
            pass
        
        self.sender = pulseio.PulseOut(self.sender_pin, frequency=self.sender_frequency, duty_cycle=self.sender_duty_cycle)
                        
class IRRECEIVER:
    def __init__(self, pin, maxlen=1000, idle_state=True):
        self.sensor = pulseio.PulseIn(pin, maxlen=maxlen, idle_state=idle_state)
        self.sensor.pause()
        self.sensor.clear()
        
    def receive_signal(self, btn, btn_pressed_val=False):
        self.sensor.resume()
        while btn.value != btn_pressed_val:
            pass
        
        self.sensor.pause()
        if len(self.sensor) == 0:
            command  = [6500, 6500, 6500, 6500]
        else:
            command =  [self.sensor[x] for x in range(len(self.sensor))]
        
        self.sensor.clear()
        return array.array("H", command)
    
    def write_signal(self, text, file, function, btn, btn_pressed_val=False):
        with open(f'/sd/codes/{file}', 'r') as f:
            codes = json.load(f)
        text.text = f"Listening for\n{function}"
        self.sensor.resume()
        while not btn.value == btn_pressed_val:
            pass
        self.sensor.pause()
        text.text = "Saving...\n"
        command = [self.sensor[x] for x in range(len(self.sensor))]
        if command == []:
            return
        text.text += str(command)[0:20]
        time.sleep(0.5)
        self.sensor.clear()
        for code in range(len(codes['codes'])):
            if codes['codes'][code]['function'] == function:
                codes['codes'][code]['code'] = command
        with open(f'/sd/codes/{file}', 'w') as f:
            json.dump(codes, f)
        text.text = ""
        while btn.value == btn_pressed_val:
            pass
        time.sleep(0.1)
            
class PIEZO:
    def __init__(self, pin):
        self.speaker = pwmio.PWMOut(pin, variable_frequency=True)
        
    def play(self, frequency, duty_cycle):
        self.speaker.frequency = frequency
        self.speaker.duty_cycle = duty_cycle
    
    def off(self):
        self.speaker.duty_cycle = 0
        
class MAX17048:
    def __init__(self, i2c):
        self.i2c = i2c
        self.sensor = adafruit_max1704x.MAX17048(i2c)
    
    def get_voltage(self, decimals=2):
        if decimals!= 0:
            return round(self.sensor.cell_voltage, decimals)
        else:
            return int(self.sensor.cell_voltage)
    
    def get_percentage(self, decimals=0):
        if decimals != 0:
            return round(self.sensor.cell_percent, decimals)
        else:
            return int(self.sensor.cell_percent)