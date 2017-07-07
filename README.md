# TLC5940
Python driver for TCL5940 16 channel PWM

This driver excludes error handling using the XERR and SOUT pins.
EEPROM writing is also unsupported and only direct register writing has been implemented to keep the driver and hardware configuration simple.

## Requirements
The Rpi.GPIO library is required along with Python 2.7 or Python 3.
Reference to the pin connections are documented in the specification at http://www.ti.com/lit/ds/symlink/tlc5940.pdf
See reference on initialistion for pin mapping.

Apart from wiring the chip to your Raspberry Pi you will need to add resistors between pin 20 IREF and ground to set the max current allowed for any of the OUTX pins where X is a pin number from 0 to 15.
To specify the required resistor use the following calculation:
> Resistance = (1.24 * 31.5) / Max-Current

So for 30mA max current (based on an LED for exampe)
> 39.06 / 0.030 = 1302 Ohms

This means a 1302 resistance between IREF and ground will provide 0.030 Amps of current.

The information can be seen on page 14 of the refernce PDF specification from Texas Instruments. 

## Example LED code

After connecting up the IC to your Raspberry PI add LEDs to the OUT pins. Note that the OUT pins are current sinks and the LED cathode will need to be connected to the pin, whilst the anode will go to VCC.

Run the code with:
> sudo python example.py

The LEDs should pulse in a train from 0 to 15 and the restart. It should run quickly.
To terminate press CTRL-C

You may experience odd effects on the LEDs after terminating. This is due to the blank pin floating and not tied to VCC or ground. Add a 10k pull up resistor to the BLANK pin so this doesn't cause flickering after reset.

## Driver API

### initialisation (__init__)
Parameters: blankpin, progpin, latchpin, gsclkpin, serialpin, clkpin

All inputs are integers expressing the pin numbers in BCM mode. Typically these numbers are the ones printed on cases and guides. Search for pin references if unsure.

#### Mapping
Format: param -> TCL5940 pin on 28-Pin PDIP layout

blankpin -> 23 BLANK
progpin -> 27 VPRG
latchpin -> 24 XLAT
gsclkpin -> 18 GSCLK
serialpin -> 26 SIN
clkpin -> 25 SCLK

### initialise()
After creating an instance of tlc5940 the initialise() function must be called to setup the GPIO.
This also resets the registers on the chip

Call this again if cleanup() has been called.

### cleanup()
Resets the GPIO. Call initialise() again to setup the driver for further use.
Note that this will not reset the registers.
You may experience some odd outputs from the IC after calling cleanup. This is due to the reset taking the pins into a default state which causes odd things to happen. This appears safe but cleanup may not provide desired effects.
Call reset() if you just want to turn off the outputs and reset the registers.

### reset()
This resets the chip registers and blanks the outputs. If LEDs are connected they will turn off.

### blank(val)
val is an integer expressing 1 or 0. If set to 1 then the outputs will be disabled. If 0 then outputs will be enabled and use the register dot and grey value settings.

### set_dot(out, value)
out is a zero based index of the output to set the dot value for. Acceptable values range from 0 to 63. Out of bound values will be set to the min or max allowable values.
A dot value is a fraction of the voltage set by resistors on the IREF pin. So if 30mA is the max output then the dot value specifies 64 fractions of this current in the acutal output. So a value of 32 delivers 15mA.

Values are only set after calling write_dot_values()

### set_grey(out, value)
out is a zero based index which references which OUT pin is specified. This matches the chip output numbering.
Acceptable values range from 0 to 4095. Any values out of this range will be set to min or max values instead of throwing an exception.

The value specifies the PWM duty as a 4096 fractions. Therefore 2048 should be 50% duty. 

### write_dot_values()
This function writes the current set of dot values to the IC register.
Call set_dot to specify what will be set.
By default all registers will default to 63 (max current).

### write_grey_values()
This funciton writes the current set of grey values to the IC register.
Call set_grey to specify values to be set
By default the max value of 4095 will be set for every OUT pin.

You must call this to update any values to the IC set through calls to set_grey

### pulse_clk()
An essential function call to make to actually see the effects of changes made.
Call this in a continuous loop to see the PWM effects on the OUT pins.

This call writes a clock cycle (4096 pulses) and then resets the PWM counter by calling blank()
In effect this function drives a single PWM pulse cycle.