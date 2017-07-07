# TLC5940 Driver for Python Copyright (C) 2017  Aidan Holmes
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# See example code for demonstration of usage and README for more information.

import RPi.GPIO as GPIO
from math import floor

class tlc5940(object):
    "Texas Instruments TLC5940 driver for Raspberry Pi"

    def __init__(self, blankpin, progpin, latchpin, gsclkpin, serialpin, clkpin):
        self._blankpin = blankpin
        self._progpin = progpin
        self._latchpin = latchpin
        self._gsclkpin = gsclkpin
        self._serialpin = serialpin
        self._clkpin = clkpin
        self._dotvalues = [0xFF] * 16
        self._greyvalues = [0xFFFF] * 16
        self._first = 1

    def initialise(self):
        'Initialise the Raspberry Pi pins and the TLC chip'
        # TLC5940 doesn't use a serial protocal. Bit banging seems to be the
        # only way to drive this chip.
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._blankpin, GPIO.OUT)
        GPIO.setup(self._progpin, GPIO.OUT)
        GPIO.setup(self._latchpin, GPIO.OUT)
        GPIO.setup(self._gsclkpin, GPIO.OUT)
        GPIO.setup(self._serialpin, GPIO.OUT)
        GPIO.setup(self._clkpin, GPIO.OUT)

        # Reset values for input and the registers
        self.reset()

    def writeserial(self, data, width):
        'Bit bang data from data array to the serial and clock pin'
        for value in data:
            for b in range (width-1, -1, -1):
                if ((1 << b) & value) > 0:
                    GPIO.output(self._serialpin, 1)
                else:
                    GPIO.output(self._serialpin, 0)
                GPIO.output(self._clkpin, 1)
                GPIO.output(self._clkpin, 0)
                
    def pulse_clk(self):
        'Bit bang the clock and blank pin'
        self.blank(1)
        self.blank(0)
        for i in range(0,4096):
            GPIO.output(self._gsclkpin, 1)
            GPIO.output(self._gsclkpin, 0)
        
    def cleanup(self):
        'Clean up GPIO and chip values'
        GPIO.cleanup()

    def reset(self):
        'Reset pin values'
        GPIO.output(self._blankpin, 1) # set high to disable output (blank)
        GPIO.output(self._progpin, 0) # high to write dot data and low for greyscale
        GPIO.output(self._latchpin, 0) # set high to complete a write to register
        GPIO.output(self._clkpin, 0)
        GPIO.output(self._serialpin, 0)
        self._dotvalues = [0x3F] * 16
        self._greyvalues = [0x0FFF] * 16
        self.write_dot_values() # initialise dot values
        self.write_grey_values() # initialise grey values
        if self._first:
            GPIO.output(self._clkpin, 1)
            GPIO.output(self._clkpin, 0)
            self._first = 0

    def blank(self, val):
        'Blank the leds, set high for leds off and low for leds on'
        GPIO.output(self._blankpin, val) 

    def set_dot(self, out, value):
        'Set a dot value for current correction, per led'
        # constrain to 6 bit value
        if value < 0: value = 0
        elif value > 63: value = 63

        # Constrain led index
        if out < 0: out = 0
        elif out > 15: out = 15

        self._dotvalues[15-out] = value

    def write_dot_values(self):
        'Send all dot values to the TLC chip'
        GPIO.output(self._progpin, 1) 
        # In theory, sleep for 10ns - VPRG to SCLK
        self.writeserial(self._dotvalues, 6) # write 6 bits of data
        # In theory, sleep for 10ns - SCLK to XLAT
        GPIO.output(self._latchpin, 1) 
        # In theory, sleep for 20ns - XLAT pulse duration
        GPIO.output(self._latchpin, 0) 
        # In theory, sleep 10ns - XLAT to VPRG (up or down)

    def set_grey(self, out, value):
        'Set a 12 bit grey value for an led'
        # constrain to 12 bit value
        if value < 0: value = 0
        elif value > 4095: value = 4095

        # Constrain out index
        if out < 0: out = 0
        elif out > 15: out = 15

        self._greyvalues[15-out] = value

    def write_grey_values(self):
        'Send all grey values to TLC chip'
        GPIO.output(self._progpin, 0) 
        # In theory, sleep for 10ns - VPRG to SCLK
        self.writeserial(self._greyvalues, 12) # write 12 bits of data
        # In theory sleep for 10ns - SCLK to XLAT
        GPIO.output(self._latchpin, 1) 
        # In theory, sleep for 20ns - XLAT pulse duration
        GPIO.output(self._latchpin, 0) 
        # In theory, sleep 10ns - XLAT to VPRG (up or down)
        


