#%%
# NOTAS
#%reset -f # Borra variables sin confirmacion

import numpy as np
from numpy import loadtxt
import matplotlib.pyplot as plt
import scipy.signal as sc
from mpldatacursor import datacursor

plt.rcParams['axes.grid'] = True

# FUNCIONES

# Dibuja una señal con su espectro
def plot_signal(signal, sig_awgn, fs, L, num):
    t = np.arange(0, len(signal)*Ts, Ts)
    # FFT de señales completas con y sin ruido
    signal_f = np.fft.fft(signal, L)
    f = np.linspace(0.0, fs/2.0, L//2)
    
    plt.figure(num)
    plt.subplot(2,1,1)
    plt.plot(t, signal)
    plt.title('Signal without noise')
    plt.ylabel('Descrete value')
    plt.xlabel('Time (s)')
    
    plt.subplot(2,1,2)
    plt.plot(f, 2.0/L * np.abs(signal_f[0:L//2]))
    plt.title('FFT of signal without noise')
    plt.ylabel('Descrete value')
    plt.xlabel('Frecuencia (Hz)')
    plt.xlim([0, 100])
    
    plt.show()

# Dibuja la señal original y la señal con ruido junto con sus espectros
def plot_signal_noise(signal, sig_awgn, fs, L, num):
    
    t = np.arange(0, len(signal)*Ts, Ts)
    # FFT de señales completas con y sin ruido
    signal_f = np.fft.fft(signal, L)
    sig_awgn_f = np.fft.fft(sig_awgn, L)
    f = np.linspace(0.0, fs/2.0, L//2)
    
    plt.figure(num)
    plt.subplot(2,2,1)
    plt.plot(t, signal)
    plt.title('Signal without noise')
    plt.ylabel('Descrete value')
    plt.xlabel('Time (s)')
    
    plt.subplot(2,2,2)
    plt.plot(f, 2.0/L * np.abs(signal_f[0:L//2]))
    plt.title('FFT of signal without noise')
    plt.ylabel('Descrete value')
    plt.xlabel('Frecuencia (Hz)')
    plt.xlim([0, 5])
    
    plt.subplot(2,2,3)
    plt.plot(t, sig_awgn)
    plt.title('Signal with noise')
    plt.ylabel('Descrete value')
    plt.xlabel('Time (s)')
    
    
    plt.subplot(2,2,4)
    plt.plot(f, 2.0/L * np.abs(sig_awgn_f[0:L//2]))
    plt.title('FFT of signal with noise')
    plt.ylabel('Descrete value')
    plt.xlabel('Frecuencia (Hz)')
    plt.xlim([0, 5])
    
    plt.show()

#------------------------------------------------------------------------------
# LECTURA DE SEÑALES Y ADICIÓN DE RUIDO

signal_b = loadtxt("signal_bint.txt", comments="#", delimiter=" ", unpack=False)
signal_h2 = loadtxt("signal_h2int.txt", comments="#", delimiter=" ", unpack=False)
signal = loadtxt("signal_bh2.txt", comments="#", delimiter=" ", unpack=False)
                    
# Adicion de ruido blanco a la señal
noise_mean = 0
noise_desv = 20;
noise = np.random.normal(noise_mean, noise_desv, len(signal))
sigb_awgn = np.around(signal_b + noise);
sigh2_awgn = np.around(signal_h2 + noise);
sig_awgn = np.around(signal + noise);

fs = 1000;
Ts = 1/fs;
t = np.arange(0, len(signal)*Ts, Ts)
L = 2**18;
signal_f = np.fft.fft(signal, L)
sig_awgn_f = np.fft.fft(sig_awgn, L)
f = np.linspace(0.0, fs/2.0, L//2)

plot_signal_noise(signal_b, sigb_awgn, fs, L, 1)
plot_signal_noise(signal_h2, sigh2_awgn, fs, L, 2)
plot_signal_noise(signal, sig_awgn, fs, L, 3)

#%% INICIO DEL PROCESAMIENTO

sig_awgn = np.around(signal + noise);

# Un ritmo cardiaco normal está en [50, 200] pulsaciones/min
# Un ritmo de respiración normal está en [10, 40] respiraciones/min
brate_max = 40
brate_min = 10
hrate_max = 200
hrate_min = 50

fL = min(brate_min, hrate_min)/60
fH = max(brate_max, hrate_max)/60
fs = 1000
fN = fs/2  # Frecuencia de Nyquist (usada en funciones para normalizar)

# Sin usar SOS
b, a = sc.butter(4, [fL/fN, 40/fN], btype='band')
w, h = sc.freqz(b, a, worN=L, fs=1000)

plt.figure(5)
plt.subplot(2,1,1)
plt.plot(w, 20 * np.log10(abs(h)), 'b')
plt.ylabel('Amplitude (dB)', color='b')
plt.xlabel('Frequency (rad/s)')
plt.xscale('log')
plt.xlim(0.001, 1000)
plt.ylim(-80, 1)
plt.subplot(2,1,2)
angles = np.unwrap(np.angle(h))
plt.plot(w, angles, 'g')
plt.ylabel('Angle (radians)', color='g')
plt.xlim(0.001, 1000)
plt.xscale('log')
plt.grid()
plt.axis('tight')
datacursor(draggable=True)
plt.show()

# Usando SOS: Mejor opción cuando se aumenta el orden del filtro
sos = sc.butter(3, [fL/fN, fH/fN], btype='band', output='sos')
w, h = sc.sosfreqz(sos, worN=L, fs=1000)

plt.figure(6)
plt.subplot(2,1,1)
plt.plot(w, 20 * np.log10(abs(h)), 'b')
plt.ylabel('Amplitude (dB)', color='b')
plt.xlabel('Frequency (rad/s)')
plt.xscale('log')
plt.xlim(0.001, 1000)
plt.ylim(-80, 1)
plt.subplot(2,1,2)
angles = np.unwrap(np.angle(h))
plt.plot(w, angles, 'g')
plt.ylabel('Angle (radians)', color='g')
plt.xlim(0.001, 1000)
plt.xscale('log')
plt.grid()
plt.axis('tight')
datacursor(draggable=True)
plt.show()

sig_awgn_filt = sc.sosfilt(sos, sig_awgn)
# sig_awgn_filt = sig_awgn_filt - min(sig_awgn_filt)
plot_signal_noise(sig_awgn, sig_awgn_filt, fs, L, 7)

sig_filt_f = np.fft.fft(sig_awgn_filt, L)
sig_filt_f = sig_filt_f[0:L//2]
maxim = max(np.abs(sig_filt_f))   # Pico maximo en el espectro (respiracion)
ibr = np.where(np.abs(sig_filt_f) == maxim)
br = f[ibr]
br_min = br*60  # Resultado del ritmo respiratorio en resp/min

#%% GENERACIÓN DE SEÑAL CUADRADA EQUIVALENTE A LA RESPIRACIÓN

threshold = np.mean( [min(sig_awgn), max(sig_awgn)] )
j = 0
k = 0
sig_sup = []
sig_inf = []

for i in range(0, len(sig_awgn)):
    if sig_awgn[i] >= threshold:
        sig_sup.append(sig_awgn[i])
    else:
        sig_inf.append(sig_awgn[i])

sig_sup = np.array(sig_sup)
sig_inf = np.array(sig_inf)
vlow = np.mean(sig_inf)
vhi = np.mean(sig_sup)
square = []

for i in range(0, len(sig_awgn)):
    if sig_awgn[i] >= threshold:
        square.append(vhi)
    else:
        square.append(vlow)
        
square = np.array(square)
plt.figure(8)
plt.plot(square)
        
    
    


#%% SEGMENTACIÓN DE LA SEÑAL PARA SIMULACIÓN DE VENTANAS

l = len(sig_awgn)  # longitud total de la señal a procesar
n_win = l//3 # numero de muestras de una ventana
iter = int(np.trunc(l/n_win))  # número de ventanas completas
resto = l % n_win        # numero elementos de última ventana

for i in range(0,iter+1):   # i toma valores entre 0 e iter
    print(i)
    if i < iter:
        y = sig_awgn[i*n_win:(i+1)*n_win]
       # plot_signal_noise(y, y, fs, L, i)
        
    else:
        y[0:resto] = sig_awgn[iter*n_win:iter*n_win+resto]
    
    
    

        


                    
        

#%%