import RPi.GPIO as GPIO 
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1x15 import Mode
from adafruit_ads1x15.analog_in import AnalogIn
import ustruct

def _write_register(self, register, value):
    data = ustruct.pack('>BH', register, value)
    self.i2c.writeto(self.address, data)

GPIO.setup(RDY, GPIO.IN, pull_up_down=GPIO.PUD_UP)

RDY = 17
RATE = 250
REGISTER_CONVERT = const(0x00)
REGISTER_CONFIG = const(0x01)
REGISTER_LOWTHRESH = const(0x02)
REGISTER_HITHRESH = const(0x03)
LOWTHRESH = const(0x0000)
HITHRESH = const(0x8000)
COMP_QUE = const(0x0000)

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P0)
ads.mode = Mode.CONTINUOUS
ads.data_rate = RATE

# Create differential input between channel 0 and 1
#chan = AnalogIn(ads, ADS.P0, ADS.P1)

print("{:>5}\t{:>5}".format('raw', 'v'))

#write_register(self, reg, value):
ads.gain = 2/3

while True:
    print("{:>5}\t{:>5.6f}".format(chan.value, chan.voltage))
    time.sleep(0.5)
