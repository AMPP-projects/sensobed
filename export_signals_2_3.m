%matriz2 = readmatrix('Pruebas adquisicion.xlsx');
t2_aux = matriz2(:,1);
s2_aux = matriz2(:,2);

t2 = [];
s2 = [];

for i = 1:length(matriz2)
    if ~isnan(s2_aux(i))
        t2(i) = t2_aux(i);
        s2(i) = s2_aux(i);
    end
end

t2 = t2';
s2 = s2';
signal2 = [t2, s2];
writematrix(signal2, 'signal_h1.txt')

signal3 = readmatrix('Pruebas adquisicion.xlsx', 'Sheet', 'Hoja2');
writematrix(signal3, 'signal_h2.txt')
