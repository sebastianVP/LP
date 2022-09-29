import digital_rf as drf


do = drf.DigitalRFReader('/media/soporte/DATA/T2/')
list_Ch=do.get_channels()
print(list_Ch)
s,e = do.get_bounds('ch0')
print(s)
data = do.read_vector(s,10,'ch0')
print(data)
