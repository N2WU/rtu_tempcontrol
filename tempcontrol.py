# -*- coding: utf-8 -*-
"""
Created on Fri May 28 08:29:57 2021

@author: Nolan

Taken from https://minimalmodbus.readthedocs.io/en/stable/usage.html
"""

#!/usr/bin/env python3
import minimalmodbus


#This part can be simplified using SSHamilton's abbreviation command for devices
instrument = minimalmodbus.Instrument('/dev/ttyUSB1', 1)  # port name, slave address (in decimal)

## From https://www.testequity.com/UserFiles/documents/pdfs/115Aman.pdf
## The actual chamber temperature reading is Modbus register 100 (Input 1 Value).
## • The static temperature set point is Modbus register 300 (Set Point 1).
## • The temperature set point during a profile is Modbus register 4122 (Set Point 1, Current Profile Status).
## • The decimal points are implied. For example, 1005 is actually 100.5 and -230 is -23.0.


## Read temperature (PV = ProcessValue) ##
temperature = instrument.read_register(100, 1)  # Registernumber, number of decimals
print(temperature)

## Change static temperature setpoint (SP) ##
NEW_TEMPERATURE = 95
instrument.write_register(300, NEW_TEMPERATURE, 1)  # Registernumber, value, number of decimals for storage


## Now to figure out what the profile option means
