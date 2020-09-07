import RPi.GPIO as GPIO 
import time
import board
import busio

#Biblioteca original
# import adafruit_ads1x15.ads1115 as ADS
# from adafruit_ads1x15.ads1x15 import Mode
# from adafruit_ads1x15.analog_in import AnalogIn

#Biblioteca modificada
import ads1115_mod.ads1115 as ADS
from ads1115_mod.ads1x15 import Mode
from ads1115_mod.analog_in import AnalogIn



def my_callback(channel):
    print('Conversion ready')

RDY = 17 # Pin de entrada del aviso CONVERSION READY
RATE = 8

GPIO.setup(RDY, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Crea el bus I2C
i2c = busio.I2C(board.SCL, board.SDA)
# Crea el objeto ADS usando el bus I2C
ads = ADS.ADS1115(i2c, ConvRdy=1)
#ads = ADS.ADS1115(i2c)
# Crea un canal de entrada "single-ended" en el canal 0
chan = AnalogIn(ads, ADS.P0)
# Establece el modo de conversión continua
ads.mode = Mode.CONTINUOUS
# Establece la tasa de muestreo
ads.data_rate = RATE
# Establece FSR
    # The ADS1015 and ADS1115 both have the same gain options.
    #
    #       GAIN    RANGE (V)
    #       ----    ---------
    #        2/3    +/- 6.144
    #          1    +/- 4.096
    #          2    +/- 2.048
    #          4    +/- 1.024
    #          8    +/- 0.512
    #         16    +/- 0.256
ads.gain = 2/3

print(chan.value) # Lectura incial para configurar el registro CONFIG

print("{:>5}\t{:>5}".format('raw', 'v'))
GPIO.add_event_detect(RDY, GPIO.FALLING, callback=my_callback)

while True:
    print("{:>5}\t{:>5.6f}".format(chan.value, chan.voltage))
    time.sleep(0.5)
