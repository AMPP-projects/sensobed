# En esta version:
# - Se muestrea pero se usan las señales de test para el procesamiento
# - Se hace segmentacion: cada cuatro resultados de hrate se saca uno de brate

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

#Biblioteca original
# import adafruit_ads1x15.ads1115 as ADS
# from adafruit_ads1x15.ads1x15 import Mode
# from adafruit_ads1x15.analog_in import AnalogIn

# Lectura de senales test
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

conv = 0 # Contador del numero de conversiones
nConv = len(yn) # Conversiones totales de una ventana
endSampling = 0
vueltas = 0
n = []
m = np.zeros(len(y))
m[1] = 1
p = []

# Rutina de interrupcion
def my_callback(channel):
    global RDY, ads, chan, conv, endSampling, nConv, vueltas
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

# Lectura inicial para configurar el registro CONFIG
print(chan.value) 
# Establece una interrupcion por flanco de bajada en el pin RDY
GPIO.add_event_detect(RDY, GPIO.FALLING, callback=my_callback)

num = 0
nSlot = 1


############### INICIALIZACION PROCESAMIENTO ####################

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

##################### FIN DEL PROCESAMIENTO  #######################


while num <= nSlot:
    #print('Entro en while num: %d' % num)
    
    ###################### PROCESAMIENTO ############################
    
    m_filt = sc.sosfilt(sos, m)
    m_filt_f = np.fft.fft(m_filt, L)
    m_filt_f = m_filt_f[0:L//2]
    
    # Pico maximo en el espectro (respiracion)
    maxim_b = max(2**8/L * np.abs(m_filt_f))
    ibr = np.where(2**8/L * np.abs(m_filt_f) == maxim_b)
    br = f[ibr]
    # Resultado del ritmo respiratorio en resp/min
    br_min = br*60
    
    # OBTENCION DE LA FRECUENCIA CARDIACA (METODO 1: restar cuadrada)
    # threshold para la creacion de la cuadrada
    threshold_b = np.mean( [min(m), max(m)] )
    m_sup = []
    m_inf = []
    # creacion de la cuadrada
    for i in range(0, len(m)):
        if m[i] >= threshold_b:
            m_sup.append(m[i])
        else:
            m_inf.append(m[i])
    # creacion del array a partir de las listas
    m_sup = np.array(m_sup)
    m_inf = np.array(m_inf)
    # medias de los vectores superiores e inferiores
    vlow = np.mean(m_inf)
    vhi = np.mean(m_sup)
    square = []

    for i in range(0, len(m)):
        if m[i] >= threshold_b:
            square.append(vhi)
        else:
            square.append(vlow)
            
    square = np.array(square)
    # Resta del espectro de la cuadrada creada
    m_f = np.fft.fft(m, L)
    square_f = np.fft.fft(square, L)
    mh_f = m_f - square_f
    # Parte positiva del espectro de la senal resta
    mh_f = mh_f[0:L//2]
    m_f = m_f[0:L//2]
    square_f = square_f[0:L//2]
    
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

    f_range = f[idx1:idx2]
    mh_f_range = mh_f[idx1:idx2]

    threshold_h = np.mean( [min(2**8/L * np.abs(mh_f_range)), max(2**8/L * np.abs(mh_f_range))] )
    maxim_h = sc.find_peaks(2**8/L * np.abs(mh_f_range), prominence=threshold_h)
    maxim_h = np.array(maxim_h[0])
    if num != 0:
        hr = f_range[maxim_h[0]]
        hr_min = hr*60
        print('Frecuencia cardiaca %d \n' % hr_min)
        print('Frec. respiratoria %d' % br_min)
    
    ############# FIN DEL PROCESAMIENTO ############################
    
    
    #print('Waiting')
    
    while endSampling == 0:
        a = 0    
    endSampling = 0
    #print('End sampling %d \n' % endSampling)
    m = n
    n = []
    m = p
    p = []
    #print('Vueltas: %d' % vueltas)
    if num < nSlot:
        GPIO.add_event_detect(RDY, GPIO.FALLING, callback=my_callback)
        print('Interrupt on')   
    num += 1
        
