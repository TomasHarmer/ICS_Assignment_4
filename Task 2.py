# TASK 2

import machine
import network
import socket
import time
from machine import I2C
from machine import Pin, ADC
from time import sleep

ap = network.WLAN (network.AP_IF)
ap.active (True)
ap.config (essid = 'ESP32-Group-15')
ap.config (authmode = 3, password = 'WiFi-password')

#define pin nums
potPinNum=34
neoPinNum=21
rLedPinNum=33
yLedPinNum=15
gLedPinNum=32
buttonPinNum=14

# potentiometer pin
# potPin = machine.Pi(potPinNum, machine.Pin.IN)

# i2c pins
sdaPin= machine.Pin(23, machine.Pin.IN)
sclPin= machine.Pin(22, machine.Pin.IN)

# configuring all the  pins to be inputs
pinsIn = [machine.Pin(i, machine.Pin.IN) for i in (buttonPinNum)]
pinsOut = [machine.Pin(i, machine.Pin.OUT) for i in (neoPinNum, rLedPinNum, yLedPinNum, gLedPinNum)]

html = """<!DOCTYPE html>
<html>
    <head> <title>ESP32 Pins</title> </head>
    <body> <h1>ESP32 Pins</h1>
        <table border="1"> <tr><th>Pin</th><th>Value</th></tr> %s </table>
    </body>
</html>
"""

# configure temp i2c sensor
i2c = machine.SoftI2C(sclPin,sdaPin,freq=400000)
tempAddress = 24

# cofigure potentiometer
pot = ADC(Pin(potPinNum))
pot.atten(ADC.ATTN_11DB)


def temp_c(temp_raw):
    # convert raw temperature data to temperature value
    
    
    
    
    temp_raw_val = (temp_raw[1] << 8) | temp_raw[0]
    temp_sign = (temp_raw_val & 0x8000) >> 15
    temp_msb = (temp_raw_val & 0x7F00) >> 8
    temp_lsb = temp_raw_val & 0xFF
    if temp_sign == 1:
        temp_val = -((~(temp_msb - 1) << 8) | temp_lsb) * 0.0625
    else:
        temp_val = ((temp_msb << 8) | temp_lsb) * 0.0625
    return (temp_val)


addr = socket.getaddrinfo('192.168.4.1', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr) # print statement 

while True:
    cl, addr = s.accept()
    print('client connected from', addr)
    cl_file = cl.makefile('rwb', 0)
    while True:
        line = cl_file.readline()
        #print(line)
        if not line or line == b'\r\n':
            break
    rows = ['<tr><td>%s</td><td>%d</td></tr>' % (str(p), p.value()) for p in pinsIn]
    rows += ['<tr><td>%s</td><td>%d</td></tr>' % (str("temp") , temp_c(i2c.readfrom_mem(tempAddress,5,2)))] # update temperature sensor value 
    rows += ['<tr><td>%s</td><td>%d</td></tr>' % (str("pot") , pot.read())] # update potentiometer value
    rows += ['<tr><td>%s</td><td>%d</td></tr>' % (str(p), p.value()) for p in pinsOut]
    response = html % '\n'.join(rows)
    cl.send(response)
    cl.close()
 
