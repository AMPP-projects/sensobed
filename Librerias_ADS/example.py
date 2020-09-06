'''
This example assumes you have set the ADS1115 address to 0x48
by connecting the ADDR pin to ground. If you have selected a
differnet address you will need to modify the constructor call
to ADS1115 to specify a different address like:

adc = ADS1115(i2c, address=0x49)

This example also assumes the default range of the ADS of
+- 4.096V. If your voltage input is in a different range
this can also be specified in the constructor call. For
example if your input voltage is within the range of +-2.048V
you would call the constructor like this:

adc = ADS1115(i2c, gain=PGA_2_048V)

A list of available gain options can be found in ADS1115.py
around line27.
'''

import pycom
from machine import I2C, Pin, Timer
from network import WLAN

from ADS1115 import ADS1115

# Use the built in LED as a status indicator
status_led = Pin('G16', mode=Pin.OUT, value=1)

# Setup ADS1115 using defaults (0x48 address and 4.096V max range)
i2c = I2C(0, I2C.MASTER)
adc = ADS1115(i2c)

def read_adc(alarm):
    if status_led:
        status_led.toggle()

    print("\nChannel 0 voltage: {}V".format(adc.get_voltage(0)))
    print("Channel 0 ADC value: {}\n".format(adc.read(0)))

def main():
    # Use the RGB LED as an indicator of WiFi status
    pycom.heartbeat(False)
    wlan = WLAN()
    if wlan.isconnected():
        pycom.rgbled(0x000f00)
    else:
        pycom.rgbled(0x0f0000)

    # Read the ADC on a 5 second interval
    Timer.Alarm(read_adc, 5, periodic=True)


main()