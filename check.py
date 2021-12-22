import numpy as np
from refguide_checker import Checker
a = np.arange(15).reshape(3, 5)
print(a)
print(a.shape)
print(a.ndim)
print(a.itemsize)
print(a.size)
print(a.dtype.name)

from scipy.signal import savgol_coeffs
print(savgol_coeffs(5, 2))
    # array([-0.08571429,  0.34285714,  0.48571429,  0.34285714, -0.08571429])

print(np.allclose([0.00000001], [0.00000002]))
print(np.allclose([0.00000001], [0.00000002], atol=0.000000001))

x = 1e-8
print(0.00000002)


print(np.allclose([0.0001], [0.0002]))
print(np.allclose([0.0001], [0.0002], atol=0.0001))

print(0.0002)

print(Checker().check_output('0', '0', []))

from doctest import OutputChecker

r = OutputChecker()
r._source
