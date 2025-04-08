import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# Input points (complex numbers)
points = np.array([1j, 2+6j, 4+3j, 2+2j])

# Extract real and imaginary parts
x = np.real(points)
y = np.imag(points)

# Parameterize the points (uniform parameterization)
t = np.linspace(0, 1, len(points))

# Create a finer parameterization for the spline
t_fine = np.linspace(0, 1, 500)

# Generate B-spline for real and imaginary parts separately
spline_x = make_interp_spline(t, x)(t_fine)
spline_y = make_interp_spline(t, y)(t_fine)

# Plot the points and the B-spline
plt.figure(figsize=(8, 6))
plt.plot(x, y, 'o', label='Original Points', color='red')  # Original points
plt.plot(spline_x, spline_y, label='B-spline Curve', linewidth=2)  # B-spline
plt.axhline(0, color='gray', linestyle='--', linewidth=0.5)
plt.axvline(0, color='gray', linestyle='--', linewidth=0.5)
plt.title("B-spline Through Complex Points")
plt.xlabel("Real Part")
plt.ylabel("Imaginary Part")
plt.legend()
plt.grid(True)
plt.show()