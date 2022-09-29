import numpy
import matplotlib.pyplot as plt
PATH     = "/home/soporte/Downloads/RM_SOPHY/data/"
#filename4 = "data_sawtooth.bin"
#filename4 = "data_sine.bin"
#filename4 = "data_triangle.bin"
#filename4 = "data_2m_sawtooth.bin"
filename4 = "data_USRP002.bin"
#filename4 = "data_USRP_tri002.bin"
dir_file = PATH+filename4
data = numpy.fromfile(open(dir_file), dtype=numpy.float32)
#fs=6*1e6
fs= 6*1e6
#fs= 20*1e6
time=numpy.arange(len(data))/(fs)
#-------------------VECTOR DE FRECUENCIA
NFFT = len(data)
f=numpy.linspace(-int(NFFT)/2,int(NFFT)/2-1,int(NFFT))*fs /NFFT # Frequency Vector
print ("LEN-DATA :",len(data))
print("fmax     :",numpy.max(f))
#------------- FFT ---------------------------------------------
data_fft= numpy.fft.fftshift(numpy.fft.fft(data))
D_F_fft = numpy.abs(data_fft)/len(f)
#--------------- creando figuras  ------------------------
fig, axes = plt.subplots(3, 1, figsize=(16,12))
ax1,ax2,ax3 =axes
ax1.plot(time[:6000],data[:6000])
ax2.plot(f[f>0],D_F_fft[f>0])
ax2.set_xlim(0,8*1e5)
#-----------------------BEAT FREQUENCY-------------
c= 3*1e8
B= 0.75*1e6
#B=  1*1e6
if filename4=="data_sawtooth.bin" or filename4=="data_2m_sawtooth.bin" or filename4 == "data_USRP002.bin":
    T=2e-3
    #T=10e-6
    #----Diente de Sierra-------
    R_C = c/(2*(B/T))
    print("FACTOR DEL BEAT SOUTH",R_C)
if filename4=="data_sine.bin" or filename4=="data_2m_sine.bin":
    T=1e-3
    #----Sine-------
    R_C = c/(12*(B/T))
    print("FACTOR DEL BEAT SINE",R_C)
if filename4=="data_triangle.bin" or filename4=="data_USRP_tri002.bin":
    T=1e-3
    #----Triangle-------
    R_C = c/(2*(B/T))
    print("FACTOR DEL BEAT Triangle",R_C)

#D_F_fft_m= numpy.roll(D_F_fft[f>0],-10300)
print("len D_F",len(D_F_fft[f>0]))
D  =  D_F_fft[f>0]
delta_r = (f[f>0][1]-f[f>0][0])*R_C
print("Range",(f[f>0][1]-f[f>0][0])*R_C)

roll_ = (50793-25000)/delta_r
roll = True
if roll == True:
    D=numpy.roll(D,-int(roll_))
    ax3.set_xlim(0,26*1e3)
print(f[f>0]*R_C)
ax3.plot(f[f>0]*R_C,D)
plt.show()
