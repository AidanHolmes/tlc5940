# TLC5940 Driver Example for Python Copyright (C) 2017  Aidan Holmes
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
# Animates leds connected to channels 0 - 15 on a TLC5940 chip
# Note the pin configuration to replicate on a Rasperry Pi

from tlc import tlc5940

leds = tlc5940(blankpin = 27,
               progpin = 22,
               latchpin = 17,
               gsclkpin = 18,
               serialpin = 23,
               clkpin = 24)

try:
    leds.initialise()

    step = 100

    intensities_val = [0] * 16
    intensities_dir = [0] * 16
    led_index = 0

    while 1:
        # Do the setting and displaying
        for led in range (0, 16):
            leds.set_grey(led, intensities_val[led]) 

        leds.write_grey_values()
        leds.pulse_clk()

        # Update LEDs
        animating = 0
        for ledval in intensities_val:
            if ledval > 0: animating = 1
        if animating == 0:
            led_index = 0
                        
        if led_index < 16 and intensities_val[led_index] == 0:
            intensities_dir[led_index] = step
            led_index += 1

        for led in range (0, 16):
            intensities_val[led] += intensities_dir[led]
            if intensities_val[led] > 4095: intensities_dir[led] = -step
            elif intensities_val[led] < 0:
                intensities_dir[led] = 0
                intensities_val[led] = 0

        
except KeyboardInterrupt:
    pass

leds.blank(1)
leds.cleanup() # may cause odd flickering due to default Rpi pin settings.
               # Comment out if necessary
