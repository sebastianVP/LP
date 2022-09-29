import numpy
import matplotlib.pyplot as plt
PATH     = "/home/soporte/Downloads/RM_SOPHY/data/"

filename = "TX_USRP.bin"
#filename4 = "data_USRP_tri002.bin"
dir_file = PATH+filename
data = numpy.fromfile(open(dir_file), dtype=numpy.float32)
#fs=6*1e6
fs= 25e6
#fs= 20*1e6
time=numpy.arange(len(data))/(fs)


fig, axes = plt.subplots(1, 1, figsize=(16,12))
ax1 =axes
ax1.plot(time[:6000],data[:6000])
plt.show()
