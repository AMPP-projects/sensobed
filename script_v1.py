# En esta version:
# - Se muestrea pero se usan las señales de test para el procesamiento
# - No se hace segmentación (el tamaño de la ventana es igual al tamaño total de las señales de test)
##########################################################################################################

import RPi.GPIO as GPIO 
import time
import board
import busio
#Biblioteca modificada
import ads1115_mod.ads1115 as ADS
import numpy as np
from ads1115_mod.ads1x15 import Mode
from ads1115_mod.analog_in import AnalogIn
from numpy import loadtxt
import scipy.signal as sc

# Biblioteca original
# import adafruit_ads1x15.ads1115 as ADS
# from adafruit_ads1x15.ads1x15 import Mode
# from adafruit_ads1x15.analog_in import AnalogIn

###############################  PREPARACION SENALES DE TEST  #############################################

signal_b = loadtxt("test_signals/original/signal_bint.txt", comments="#", delimiter=" ", unpack=False)
signal_h2 = loadtxt("test_signals/original/signal_h2int.txt", comments="#", delimiter=" ", unpack=False)
y = signal_b + signal_h2

# Adicion de ruido blanco a la senal
noise_mean = 0
noise_desv = 0
noise = np.random.normal(noise_mean, noise_desv, len(y))
y = 2**15/np.max(y) * y
yn = np.around(y + noise)
print('Longitud %d \n' % len(yn))

############################# FIN PREPARACION SENALES DE TEST  ############################################

conv = 0 # Contador del numero de conversiones
nConv = len(yn) # Conversiones totales de una ventana
endSampling = 0
vueltas = 0
n = []
m = np.zeros(len(y))
m[1] = 1
p = []

#####################################  CONFIGURACION ADC  ##################################

RDY = 17 # Pin de entrada del aviso CONVERSION READY
RATE = 860 # Tasa de muestreo (SPS)
# Establece pin de entrada RDY
GPIO.setup(RDY, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# Crea el bus I2C
i2c = busio.I2C(board.SCL, board.SDA)
# Crea el objeto ADS usando el bus I2C
ads = ADS.ADS1115(i2c, ConvRdy=1)
#ads = ADS.ADS1115(i2c)
# Crea un canal de entrada "single-ended" en el canal 0
chan = AnalogIn(ads, ADS.P0)
# Establece el modo de conversion continua
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

################################### FIN CONFIGURACION ADC  ###############################

# Lectura inicial para configurar el registro CONFIG
print('Lectura inicial %d' % chan.value) 


########################### INICIALIZACION PROCESAMIENTO #################################

# Un ritmo cardiaco normal esta en [50, 200] pulsaciones/min
# Un ritmo de respiracion normal esta en [10, 40] respiraciones/min
brate_max = 40
brate_min = 10
hrate_max = 200
hrate_min = 50
# Primero, se filtra para obtener datos de la respiracion (no nos importa
# degradar las frecuencias del corazon)
fL = brate_min/60
fH = brate_max/60
fs = 1000
fN = fs/2  # Frecuencia de Nyquist (usada en funciones para normalizar)

# Usando SOS: Mejor opcion cuando se aumenta el orden del filtro
L = 2**16
f = np.linspace(0.0, fs/2.0, L//2)
sos = sc.butter(3, [fL/fN, fH/fN], btype='band', output='sos')
#sos = sc.butter(3, fH/fN, btype='low', output='sos')
w, h = sc.sosfreqz(sos, worN=L, fs=1000)

########################## FIN INICIALIZACION PROCESAMIENTO  ##########################


#####################  RUTINA INTERRUPCION ############################################

def my_callback(channel):
    global RDY, ads, chan, conv, endSampling, nConv, vueltas
    if (conv % 1000) == 0:
        print(conv)
    n.append(int(chan.value))
    p.append(yn[conv])
    conv += 1
    
    if conv == nConv:
        # apaga conversiones
        conv = 0
        GPIO.remove_event_detect(RDY)
        print('Interrupt off')
        endSampling = 1
        print('End sampling %d \n' % endSampling)
        
#####################  FIN RUTINA INTERRUPCION ###########################################

# Establece una interrupcion por flanco de bajada en el pin RDY
GPIO.add_event_detect(RDY, GPIO.FALLING, callback=my_callback)

num = 0
nSlot = 1

while num <= nSlot:
    #print('Entro en while num: %d' % num)
    
    ######################################### PROCESAMIENTO ########################################
    
    mFilt = sc.sosfilt(sos, m)
    mFiltF = np.fft.fft(mFilt, L)
    mFiltF = mFiltF[0:L//2]
   
    # Pico maximo en el espectro (respiracion)
    maxim_b = max( np.abs(mFiltF))
    ibr = np.where(np.abs(mFiltF) == maxim_b)
    br = f[ibr]
    # Resultado del ritmo respiratorio en resp/min
    brMinute = br*60
    
    # OBTENCION DE LA FRECUENCIA CARDIACA (METODO 1: restar cuadrada)
    # threshold para la creacion de la cuadrada
    threshold_b = np.mean( [min(m), max(m)] )
    mSup = []
    mInf = []
    # creacion de la cuadrada
    for i in range(0, len(m)):
        if m[i] >= threshold_b:
            mSup.append(m[i])
        else:
            mInf.append(m[i])
    # creacion del array a partir de las listas
    mSup = np.array(mSup)
    mInf = np.array(mInf)
    # medias de los vectores superiores e inferiores
    vlow = np.mean(mInf)
    vhi = np.mean(mSup)
    square = []

    for i in range(0, len(m)):
        if m[i] >= threshold_b:
            square.append(vhi)
        else:
            square.append(vlow)
            
    square = np.array(square)
    # Resta del espectro de la cuadrada creada
    mF = np.fft.fft(m, L)
    squareF = np.fft.fft(square, L)
    mhF = mF - squareF
    # Parte positiva del espectro de la senal resta
    mhF = mhF[0:L//2]
    mF = mF[0:L//2]
    squareF = squareF[0:L//2]
    # Restringe el espectro de la senal cardiaca a fh_min y fh_max
    fh_min = hrate_min/60
    fh_max = hrate_max/60
    dist1 = np.abs(f-fh_min)
    min1 = np.min(dist1)
    idx1 = np.where(dist1 == min1)
    idx1 = idx1[0]
    idx1 = idx1[0]
    dist2 = np.abs(f-fh_max)
    min2 = np.min(dist2)
    idx2 = np.where(dist2 == min2)
    idx2 = idx2[0]
    idx2 = idx2[0]

    fRange = f[idx1:idx2]
    mhFRange = mhF[idx1:idx2]
    # Obtiene umbral a partir de hacer la media al valor mínimo y máximo del espectro de la senal cardiaca
    threshold_h = np.mean( [min(np.abs(mhFRange)), max(np.abs(mhFRange))] )
    maxim_h = sc.find_peaks(np.abs(mhFRange), prominence=threshold_h)
    maxim_h = maxim_h[0] # Nos quedamos con el primer maximo del espectro
    if slot == 0:
        print('No hay resultados disponibles')
    else:  # Solo si al menos se ha muestreado una vez se sacan resultados
        hr = fRange[maxim_h[0]]
        hrMinute = hr*60
        print('Frecuencia cardiaca: %d \n' % hrMinute)
        print('Frec. respiratoria: %d' % brMinute)
    
    ############# FIN DEL PROCESAMIENTO ################################################################
    
    # Espera a que termine el muestreo (entra en caso de que el procesamiento sea mas rapido)
    while endSampling == 0:
        p
    
    endSampling = 0
    #print('End sampling %d \n' % endSampling)
    # Transfiere muestras actuales a muestras anteriores
    m = n
    n = []
    m = p
    p = []
    #print('Vueltas: %d' % vueltas)
    if slot < nSlot:
        GPIO.add_event_detect(RDY, GPIO.FALLING, callback=my_callback)
        print('Interrupt on')   
    slot += 1
    
