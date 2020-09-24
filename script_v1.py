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


############### INICIALIZACIÓN PROCESAMIENTO ####################

# Un ritmo cardiaco normal está en [50, 200] pulsaciones/min
# Un ritmo de respiración normal está en [10, 40] respiraciones/min
brate_max = 40
brate_min = 10
hrate_max = 200
hrate_min = 50
# Primero, se filtra para obtener datos de la respiración (no nos importa
# degradar las frecuencias del corazón)
fL = brate_min/60
fH = brate_max/60
fs = 1000
fN = fs/2  # Frecuencia de Nyquist (usada en funciones para normalizar)

# Usando SOS: Mejor opción cuando se aumenta el orden del filtro
sos = sc.butter(3, [fL/fN, fH/fN], btype='band', output='sos')
#sos = sc.butter(3, fH/fN, btype='low', output='sos')
w, h = sc.sosfreqz(sos, worN=L, fs=1000)

##################### FIN DEL PROCESAMIENTO  #######################


while num <= nSlot:
    print('Entro en while num: %d' % num)
    
    ###################### PROCESAMIENTO ############################
    
    n_1_filt = sc.sosfilt(sos, n_1)
    n_1_filt_f = np.fft.fft(n_1_filt, L)
    n_1_filt_f = n_1_filt_f[0:L//2]
    
    # Pico maximo en el espectro (respiracion)
    maxim_b = max(2**8/L * np.abs(n_1_filt_f))
    ibr = np.where(2**8/L * np.abs(n_1_filt_f) == maxim_b)
    br = f[ibr]
    
    # Resultado del ritmo respiratorio en resp/min
    br_min = br*60
    
    # OBTENCIÓN DE LA FRECUENCIA CARDÍACA (MÉTODO 1: restar cuadrada)
    # threshold para la creación de la cuadrada
    threshold_b = np.mean( [min(n_1), max(n_1)] )
    n_1_sup = []
    n_1_inf = []
    # creación de la cuadrada
    for i in range(0, len(n_1)):
        if n_1[i] >= threshold_b:
            n_1_sup.append(n_1[i])
        else:
            n_1_inf.append(n_1[i])
    # creación del array a partir de las listas
    y_sup = np.array(n_1_sup)
    y_inf = np.array(n_1_inf)
    # medias de los vectores superiores e inferiores
    vlow = np.mean(n_1_inf)
    vhi = np.mean(n_1_sup)
    square = []

    for i in range(0, len(n_1)):
        if n_1[i] >= threshold_b:
            square.append(vhi)
        else:
            square.append(vlow)
            
    square = np.array(square)
    # Resta del espectro de la cuadrada creada
    n_1_f = np.fft.fft(n_1, L)
    square_f = np.fft.fft(square, L)
    n_1_h_f = n_1_f - square_f
    # Parte positiva del espectro de la señal resta
    n_1_h_f = n_1_h_f[0:L//2]
    n_1_f = n_1_f[0:L//2]
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
    yh_f_range = yh_f[idx1:idx2]

    threshold_h = np.mean( [min(2**8/L * np.abs(yh_f_range)), max(2**8/L * np.abs(yh_f_range))] )
    maxim_h = sc.find_peaks(2**8/L * np.abs(yh_f_range), prominence=threshold_h)
    maxim_h = np.array(maxim_h[0])
    hr = f_range[maxim_h[0]]
    hr_min = hr*60
    
    ############# FIN DEL PROCESAMIENTO ############################
    
    
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
        
