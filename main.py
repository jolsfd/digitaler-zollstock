from machine import I2C, Pin
from hcsr04 import HCSR04

import time
import random
import machine

# I2C device address
addr = 0x70
OSCILLATOR = 0x20
DISPLAY = 0x80
# addresses for 4 digits
DIGITS = [0x00,0x02,0x06,0x08]
POINTS = 0x04 # address for time points
# digits in binary commands
NUMS = {"0": 0x3F,"1": 0x06, "2": 0x5B, "3": 0x4F, "4": 0x66, "5": 0x6D, "6": 0x7D, "7": 0x07, "8": 0x7F, "9": 0x6F}

class FourDigit:
    def __init__(self,sda=Pin(22),scl=Pin(23),freq=40000,i2c_id=0):
        # init I2C main node
        self.i2c = I2C(i2c_id,sda=sda,scl=scl,freq=freq)
        
        # check for device
        if addr not in self.i2c.scan():
            return "device not found"
        
        # init display
        # 0x01 letztes Bit auf 1
        self.i2c.writeto(addr, bytes([OSCILLATOR|0x01])) # oscillator on
        self.i2c.writeto(addr, bytes([DISPLAY|0x01])) # display on
        self.current = [0]*len(DIGITS)
        
        self.clear()
        
    def clear(self):
        for i in range(0x10): # range(16)
            self.i2c.writeto_mem(addr,i,bytes([0x00]))
            
    def write_float(self,num):
        num = str(num)

        count = 0
        for i in range(len(num)):
            if num[i] == ".":
                continue
            if count == 4:
                break
            
            data = NUMS[num[i]]
            
            if i < len(num)-1:
                if num[i+1] == ".":
                    data = data|0x80
                
            self.i2c.writeto_mem(addr,DIGITS[count],bytes([data]))
            count += 1
            
    def display_float(self,num):
        num = str(num)
        digits_written = 0
        new = [0]*len(DIGITS)
        
        for i in range(len(num)-1,-1,-1):
            if num[i] == ".":
                continue
            if digits_written == 4:
                break
            data = NUMS[num[i]]
                    
            if i < len(num)-1:
                if num[i+1] == ".":
                    data = data|0x80
                    #print("point")
                            
            #self.i2c.writeto_mem(addr,DIGITS[len(DIGITS)-1-digits_written],bytes([data]))
            new[len(DIGITS)-1-digits_written] = data
            #print(f"Writing digit {num[i]} to digit {len(DIGITS)-1-digits_written}")
            digits_written += 1
        
        #print(self.current)
        for i in range(len(DIGITS)):
            if new[i] != self.current[i]:
                self.i2c.writeto_mem(addr,DIGITS[i],bytes([new[i]]))
                #print("updating")
                
        self.current = new
            
    def test(self):
        for i in range(4):
            self.i2c.writeto_mem(addr,DIGITS[i],bytes([NUMS["8"]|0x80]))
        self.i2c.writeto_mem(addr,POINTS,bytes([NUMS["8"]|0x80]))
        
display = FourDigit()
display.test()
time.sleep(1)
display.clear()

#display.display_float(13.14)
#time.sleep(1)
#display.display_float(3.89)

sensor = HCSR04(trigger_pin=18, echo_pin=19)

while True:
    distance = sensor.distance_cm()

    display.display_float(round(distance,1))
    #print('Distance:', round(distance,1), 'cm')
    time.sleep(0.1)
    #display.clear()
