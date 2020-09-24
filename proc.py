#%%
# NOTAS
#%reset -f # Borra variables sin confirmacion

import numpy as np
from numpy import loadtxt
import matplotlib.pyplot as plt
import scipy.signal as sc
import neurokit2 as nk
from mpldatacursor import datacursor

plt.rcParams['axes.grid'] = True

plt.close('all')

# FUNCIONES

# Dibuja una señal con su espectro
def plot_signal(signal, fs, L, num, title):
    t = np.arange(0, len(signal)*Ts, Ts)
    # FFT de señales completas con y sin ruido
    signal_f = np.fft.fft(signal, L)
    f = np.linspace(0.0, fs/2.0, L//2)
    
    plt.figure(num)
    plt.suptitle(title)
    plt.subplot(2,1,1)
    plt.plot(t, signal)
    plt.title('Time signal')
    plt.ylabel('Descrete value')
    plt.xlabel('Time (s)')
    
    plt.subplot(2,1,2)
    plt.plot(f, 2**8/L * np.abs(signal_f[0:L//2]))
    plt.title('Signal FFT')
    plt.ylabel('Descrete value')
    plt.xlabel('Frecuencia (Hz)')
    plt.xlim([0, 5])
    
    plt.show()

# Dibuja dos señales y sus espectros
def plot_signals(sig1, sig2, fs, L, num, title):
    
    t = np.arange(0, len(sig1)*Ts, Ts)
    # FFT de señales completas con y sin ruido
    sig1_f = np.fft.fft(sig1, L)
    sig2_f = np.fft.fft(sig2, L)
    f = np.linspace(0.0, fs/2.0, L//2)
    
    plt.figure(num)
    plt.suptitle(title)
    plt.subplot(2,2,1)
    plt.plot(t, sig1)
    plt.title('Signal 1 in time')
    plt.ylabel('Descrete value')
    plt.xlabel('Time (s)')
    
    plt.subplot(2,2,2)
    plt.plot(f, 2**8/L * np.abs(sig1_f[0:L//2]))
    plt.title('Signal 1 FFT')
    plt.ylabel('Descrete value')
    plt.xlabel('Frecuencia (Hz)')
    plt.xlim([0, 5])
    
    plt.subplot(2,2,3)
    plt.plot(t, sig2)
    plt.title('Signal 2 in time')
    plt.ylabel('Descrete value')
    plt.xlabel('Time (s)')
    
    
    plt.subplot(2,2,4)
    plt.plot(f, 2**8/L * np.abs(sig2_f[0:L//2]))
    plt.title('Signal 2 FFT')
    plt.ylabel('Descrete value')
    plt.xlabel('Frecuencia (Hz)')
    plt.xlim([0, 5])
    
    plt.show()

#------------------------------------------------------------------------------
# LECTURA DE SEÑALES Y ADICIÓN DE RUIDO

signal_b = loadtxt("test_signals/original/signal_bint.txt", comments="#", delimiter=" ", unpack=False)
signal_h2 = loadtxt("test_signals/original/signal_h2int.txt", comments="#", delimiter=" ", unpack=False)
amp = max(signal_b)/max(signal_h2)
fs = 1000

if test == 1:
    signal_b = k*signal_b

elif test == 2:
    signal_h2 = k*signal_h2

signal = signal_b + signal_h2

# Adicion de ruido blanco a la señal
noise_mean = 0
noise_desv = 0
noise = np.random.normal(noise_mean, noise_desv, len(signal))
sigb_awgn = np.around(signal_b + noise)
sigh2_awgn = np.around(signal_h2 + noise)
sig_awgn = np.around(signal + noise)
norm = np.max(sig_awgn)

Ts = 1/fs
t = np.arange(0, len(signal)*Ts, Ts)
L = 2**18
signal_f = np.fft.fft(signal, L)
sig_awgn_f = np.fft.fft(sig_awgn, L)
f = np.linspace(0.0, fs/2.0, L//2)

plot_signals(signal_b/norm, sigb_awgn/norm, fs, L, 1, 'Breathing signal with and without noise')
plot_signals(signal_h2/norm, sigh2_awgn/norm, fs, L, 2, 'Heart signal with and without noise')
plot_signals(signal/norm, sig_awgn/norm, fs, L, 3, 'Total signal with and without noise')

#%% OBTENCIÓN DE LA FRECUENCIA RESPIRATORIA

for i in range(5,8):
    plt.close(i)

y = np.around(signal + noise)
y = y/np.max(y)

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

# Sin usar SOS
b, a = sc.butter(3, [fL/fN, fH/fN], btype='band')
w, h = sc.freqz(b, a, worN=L, fs=1000)

plt.figure(5)
plt.subplot(2,1,1)
plt.plot(w, 20 * np.log10(abs(h)), 'b')
plt.ylabel('Amplitude (dB)', color='b')
plt.xlabel('Frequency (Hz)')
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
#sos = sc.butter(3, [fL/fN, fH/fN], btype='band', output='sos')
sos = sc.butter(3, fH/fN, btype='low', output='sos')
w, h = sc.sosfreqz(sos, worN=L, fs=1000)

plt.figure(6)
plt.subplot(2,1,1)
plt.plot(w, 20 * np.log10(abs(h)), 'b')
plt.ylabel('Amplitude (dB)', color='b')
plt.xlabel('Frequency (Hz)')
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


y_filt = sc.sosfilt(sos, y)
plot_signals(y, y_filt, fs, L, 7, 'Unfiltered and filtered signals')

y_filt_f = np.fft.fft(y_filt, L)
y_filt_f = y_filt_f[0:L//2]
maxim_b = max(2**8/L * np.abs(y_filt_f))   # Pico maximo en el espectro (respiracion)
ibr = np.where(2**8/L * np.abs(y_filt_f) == maxim_b)
br = f[ibr]
br_min = br*60  # Resultado del ritmo respiratorio en resp/min

#%% OBTENCIÓN DE LA FRECUENCIA CARDÍACA (MÉTODO 1)

for i in range(8, 10):
    plt.close(i)

threshold_b = np.mean( [min(y), max(y)] )
y_sup = []
y_inf = []

for i in range(0, len(y)):
    if y[i] >= threshold_b:
        y_sup.append(y[i])
    else:
        y_inf.append(y[i])

y_sup = np.array(y_sup)
y_inf = np.array(y_inf)
vlow = np.mean(y_inf)
vhi = np.mean(y_sup)
square = []

for i in range(0, len(y)):
    if y[i] >= threshold_b:
        square.append(vhi)
    else:
        square.append(vlow)
        
square = np.array(square)
plot_signal(square, 1000, L, 8, 'Generated square signal')

y_f = np.fft.fft(y, L)
square_f = np.fft.fft(square, L)
yh_f = y_f - square_f
yh_f = yh_f[0:L//2]
y_f = y_f[0:L//2]
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

plt.figure(9)
plt.subplot(3,1,1)
plt.plot(f, 2**8/L * np.abs(y_f))
plt.xlim(0, 5)
plt.title('Global signal spectre')

plt.subplot(3,1,2)
plt.plot(f, 2**8/L * np.abs(square_f))
plt.xlim(0, 5)
plt.title('Square signal spectre')

plt.subplot(3,1,3)
plt.plot(f_range, 2**8/L * np.abs(yh_f_range))
plt.plot(f_range[maxim_h], 2**8/L * np.abs(yh_f_range[maxim_h]), "x")
plt.title('Global - square signal spectre')
plt.xlim(0, 5)
hr = f_range[maxim_h[0]]
hr_min = hr*60


#%% OBTENCIÓN DE LA FRECUENCIA CARDÍACA (MÉTODO 2)

for i in range(8, 10):
    plt.close(i)

i_sup = sc.find_peaks(y_filt)
i_inf = sc.find_peaks(-y_filt)
i_sup = np.array(i_sup[0])
i_inf = np.array(i_inf[0])

vhi = np.mean(y_filt[i_sup])
vlow = np.mean(y_filt[i_inf])
threshold_b = np.mean( [vhi, vlow] )
square = []

for i in range(0, len(y)):
    if y_filt[i] >= threshold_b:
        square.append(vhi)
    else:
        square.append(vlow)
        
square = np.array(square)
plot_signal(square, 1000, L, 8, 'Generated square signal')

y_f = np.fft.fft(y, L)
square_f = np.fft.fft(square, L)
yh_f = np.abs(y_f) - np.abs(square_f)
yh_f = yh_f[0:L//2]
y_f = y_f[0:L//2]
square_f = square_f[0:L//2]
threshold_h = np.mean( [min(2**8/L * yh_f), max(2**8/L * yh_f)] )
maxim_h = sc.find_peaks(2**8/L * yh_f, prominence=threshold_h)
maxim_h = np.array(maxim_h[0])

plt.figure(9)
plt.subplot(3,1,1)
plt.plot(f, 2**8/L * np.abs(y_f))
plt.xlim(0, 5)
plt.title('Global signal spectre')

plt.subplot(3,1,2)
plt.plot(f, 2**8/L * np.abs(square_f))
plt.xlim(0, 5)
plt.title('Square signal spectre')

plt.subplot(3,1,3)
plt.plot(f, 2**8/L * yh_f)
# plt.plot(f[maxim_h], 2**8/L * yh_f[maxim_h], "x")
plt.title('Global - square signal spectre')
plt.xlim(0, 5)
hr = f[maxim_h[0]]
hr_min = hr*60




#%% SEGMENTACIÓN DE LA SEÑAL PARA SIMULACIÓN DE VENTANAS

l = len(sig_awgn)  # longitud total de la señal a procesar
n_win = l//3 # numero de muestras de una ventana
iter = int(np.trunc(l/n_win))  # número de ventanas completas
resto = l % n_win        # numero elementos de última ventana

for i in range(0,iter+1):   # i toma valores entre 0 e iter
    if i < iter:
        y = sig_awgn[i*n_win:(i+1)*n_win]
       # plot_signals(y, y, fs, L, i)
        
    else:
        y[0:resto] = sig_awgn[iter*n_win:iter*n_win+resto]
    
    
    

                    
        

#%%
test = 1
k = 2
runcell(1)
runcell(2)
runcell(3)

#%%
test = 0
k = 1
runcell(1)
runcell(2)
runcell(4)