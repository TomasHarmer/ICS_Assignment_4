# ICS_Assignment_4
In task 2 we implemented sensors connected to a webserver which displays a table which displays the outputs from multiple temperature values. 

In task 3 we implemented a server which outputs a JSON web API which can be used to extract the state of sensors on the board; including the state of all the LEDs as well as both buttons. 
It is also possible to check the sensor values of the temperature and potentiometer. 
Changing the state of the LEDs can be done with the /led/"colour"/"state"  resource identifier; for example /led/red/on turns the red LED on, and /led/yellow/off will turn the yellow LED on. 
