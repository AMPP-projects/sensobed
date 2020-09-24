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

conv = 0 # Contador del número de conversiones
nConv = 5 # Conversiones totales de una ventana
endSampling = 0
vueltas = 0
n = []
n_1 = []

# Rutina de interrupción
def my_callback(channel):
    global RDY, ads, chan, conv, endSampling, nConv, vueltas
    conv += 1
    print(conv)
    n.append(int(chan.value))
    
    if conv == nConv:
        # apaga conversiones
        conv = 0
        vueltas += 1
        print('Vuelta: %d \n' % vueltas)
        GPIO.remove_event_detect(RDY)
        print('Interrupt off')
        endSampling = 1
        print('End sampling %d \n' % endSampling)

RDY = 17 # Pin de entrada del aviso CONVERSION READY
RATE = 8 # Tasa de muestreo (SPS)

# Establece pin de entrada RDY
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

# Lectura inicial para configurar el registro CONFIG
print(chan.value) 
# Establece una interrupción por flanco de bajada en el pin RDY
GPIO.add_event_detect(RDY, GPIO.FALLING, callback=my_callback)

num = 0
nVueltas = 3
nSlot = 3

while num <= nSlot:
    print('Entro en while num: %d' % num)
    
    # PROCESAMIENTO
    
    
    
    # FIN DEL PROCESAMIENTO
    
    
    print('Waiting')
    
    while endSampling == 0:
        a = 0    
    endSampling = 0
    print('End sampling %d \n' % endSampling)
    n_1 = n
    n = []
    #print('Vueltas: %d' % vueltas)
    if num < nSlot:
        GPIO.add_event_detect(RDY, GPIO.FALLING, callback=my_callback)
        print('Interrupt on')   
    num += 1
        
