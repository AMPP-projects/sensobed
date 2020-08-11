function [] = plot_signal(senal,fs, titl)

Ts = 1/fs;
L = 2^16;
t = 0:Ts:(length(senal)-1)*Ts;
senal_f = fft(senal, L);
senal_f = senal_f(1:L/2);
%f= fs*(0:(L/2-1))/L;
f = linspace(0.0, fs/2.0, floor(L/2));

figure
subplot(211)
plot(t,senal)
xlabel('Tiempo (s)')
ylabel('Amplitud')
title(strcat('Señal ', titl, ' en el tiempo'))

subplot(212)
plot(f,2/L * abs(senal_f))
xlabel('Frecuencia (s)')
ylabel('Amplitud')
title(strcat('Señal ', titl ,' en frecuencia'))
xlim([0,5])


end

