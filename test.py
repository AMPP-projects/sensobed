import numpy as np

fileN_1 = open("sample/n-1.txt", "r+")
samples = fileN_1.read()
fileN_1.close()
#procSamples = samples*2


# INICIALIZACIóN
# Se transfieren las muestras n a las n-1
fileN = open("sample/n.txt", "r+")
newSamples = fileN.read()
fileN.truncate(0)
fileN.close()

fileN_1 = open("sample/n-1.txt", "w+")
fileN_1.write(newSamples)
fileN_1.close()
