#TASK 3

import machine
import network
import socket
import time
import socket
import ujson as json
from machine import I2C
from machine import Pin, ADC
from time import sleep

ap = network.WLAN (network.AP_IF)
ap.active (True)
ap.config (essid = 'ESP32-Group-15')
ap.config (authmode = 3, password = 'WiFi-password')

# define pin nums
potPinNum=34
neoPinNum=21
rLedPinNum=33
yLedPinNum=15
gLedPinNum=32
buttonPinNum1=14
buttonPinNum2=16

# potentiometer pin
# potPin = machine.Pi(potPinNum, machine.Pin.IN)

# i2c pins
sdaPin= machine.Pin(23, machine.Pin.IN)
sclPin= machine.Pin(22, machine.Pin.IN)

# configuring all the  pins to be inputs
pinsIn = [machine.Pin(i, machine.Pin.IN) for i in (buttonPinNum1,buttonPinNum2)]
pinsOut = [machine.Pin(i, machine.Pin.OUT) for i in (neoPinNum, rLedPinNum, yLedPinNum, gLedPinNum)]


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



# Define a function to handle incoming requests
def handle_request(request):
    # Extract the request method and path
    method, path, *_ = request.split()

    # Check if the request method is GET and the path starts with "/data/"
#     if method == "GET" and path.startswith("/data/"):
#         # Extract the requested file name from the path
#         file_name = path.split("/")[-1]
# 
#         # Load the JSON data from the file
#         with open(file_name + ".json") as f:
#             data = json.load(f)
    if method == "GET" and path.startswith("/pins"):
        # create dictionary of pin names and values
        pinStates = {}
        pinsList = pinsIn + pinsOut
        for pin in pinsList:
            pinStates[str(pin)] = pin.value()
        data = pinStates
        return "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n" + json.dumps(data)
    
    elif method == "GET" and path.startswith("/sensors"):
        data = {"temperature": temp_c(i2c.readfrom_mem(tempAddress,5,2)), "potentiomenter": pot.read()}  
        # Return the JSON data as the response
        return "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n" + json.dumps(data)
    
    
    elif method == "GET" and path.startswith("/led/"):
        # Extract the LED color and state from the path
        _, _, color, state = path.split("/")

        # Find the corresponding LED pin based on the color
        if color == "red":
            led_pin = pinsOut[1]
        elif color == "yellow":
            led_pin = pinsOut[2]
        elif color == "green":
            led_pin = pinsOut[3]
        else:
            return "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nInvalid LED color"

        # Turn the LED on or off based on the state
        if state == "on":
            led_pin.value(1)
            msg = f"{color.upper()} LED turned ON"
        elif state == "off":
            led_pin.value(0)
            msg = f"{color.upper()} LED turned OFF"
        else:
            return "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nInvalid LED state"

        # Return the message as the response
        return "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n" + msg

    # If the request method or path is not recognized, return a 404 error
    else:
        return "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\n404 Not Found"

# Set up the server socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
server_sock = socket.socket()
server_sock.bind(addr)
server_sock.listen(1)

# Wait for incoming connections and handle them
while True:
    print("Waiting for connection...")
    client_sock, client_addr = server_sock.accept()
    print("Client connected:", client_addr)

    # Read the incoming request from the client socket98
    request = client_sock.recv(1024).decode('utf-8')
    print("Request received:")
    print(request)

    # Handle the request and send the response back to the client
    response = handle_request(request)
    print("Response:")
    print(response)
    client_sock.send(response.encode('utf-8'))

    # Close the client socket
    client_sock.close()
