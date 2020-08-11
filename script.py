
# NOTAS
#%reset -f # Borra variables sin confirmacion

import numpy as np
from numpy import loadtxt
import matplotlib.pyplot as plt
import scipy.signal as sc

plt.rcParams['axes.grid'] = True

# FUNCIONES
        
# Dibuja la señal original y la señal con ruido junto con sus espectros
def plot_signal(signal, sig_awgn, fs, L, num):
    
    t = np.arange(0, len(signal)*Ts, Ts)
    # FFT de señales completas con y sin ruido
    signal_f = np.fft.fft(signal, L)
    sig_awgn_f = np.fft.fft(sig_awgn, 2**16)
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
    plt.xlabel('Time (s)')
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
    plt.xlabel('f (Hz)')
    plt.xlim([0, 5])
    
    plt.show()


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
L = 2**16;
signal_f = np.fft.fft(signal, L)
sig_awgn_f = np.fft.fft(sig_awgn, 2**16)
f = np.linspace(0.0, fs/2.0, L//2)

plot_signal(signal_b, sigb_awgn, fs, L, 1)
plot_signal(signal_h2, sigh2_awgn, fs, L, 2)
plot_signal(signal, sig_awgn, fs, L, 3)


#%% Inicio del procesamiento

l = len(sig_awgn)  # longitud total de la señal a procesar
n_win = l//3 # numero de muestras de una ventana
iter = int(np.trunc(l/n_win))  # número de ventanas completas
resto = l % n_win        # numero elementos de última ventana

for i in range(0,iter+1):   # i toma valores entre 0 e iter
    print(i)
    if i < iter:
        y = sig_awgn[i*n_win:(i+1)*n_win]
        plot_signal(y, y, fs, L, i)
        
    else:
        y[0:resto] = sig_awgn[iter*n_win:iter*n_win+resto]
    
    
    

        


                    
        

#%%