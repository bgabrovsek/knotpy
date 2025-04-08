import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import BSpline

# Input: Control points (complex numbers)
control_points = np.array([1j, 2+6j, 4+3j, 2+2j])
control_points = np.array([1j, 2+6j])

# Extract real and imaginary parts
x = np.real(control_points)
y = np.imag(control_points)

# Define the degree of the spline (e.g., cubic)
k = 1

# Define the knot vector (uniform knots, ensuring valid spline)
n = len(control_points)  # Number of control points
t = np.concatenate(([0] * k, np.linspace(0, 1, n - k + 1), [1] * k))

# Parameterize the spline
t_fine = np.linspace(0, 1, 20)  # Fine sampling for smooth curve

# Create B-spline for real and imaginary parts
spline_x = BSpline(t, x, k)(t_fine)  # B-spline for x
spline_y = BSpline(t, y, k)(t_fine)  # B-spline for y

# Plot the control points and the B-spline
plt.figure(figsize=(8, 6))
plt.plot(x, y, 'o-', label='Control Points', color='red')  # Control points
plt.plot(spline_x, spline_y, label='B-spline Curve', linewidth=2)  # B-spline
plt.axhline(0, color='gray', linestyle='--', linewidth=0.5)
plt.axvline(0, color='gray', linestyle='--', linewidth=0.5)
plt.title("B-spline Curve (Not Passing Through Control Points)")
plt.xlabel("Real Part")
plt.ylabel("Imaginary Part")
plt.legend()
plt.grid(True)
plt.show()