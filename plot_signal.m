function [] = plot_signal(senal,fs, titl)

Ts = 1/fs;
t = 0:Ts:(length(senal)-1)*Ts;
L = 2^16;
senal_f = fft(senal, L);
senal_f = senal_f(1:L/2);
f= fs*(0:(L/2-1))/L;

figure
subplot(211)
plot(t,senal)
xlabel('Tiempo (s)')
ylabel('Amplitud')
title(strcat('Señal ', titl, ' en el tiempo'))

subplot(212)
plot(f,20*log10(abs(senal_f)))
xlabel('Frecuencia (s)')
ylabel('Amplitud')
title(strcat('Señal ', titl ,' en frecuencia'))


end

