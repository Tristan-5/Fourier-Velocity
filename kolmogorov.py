import numpy as np
import matplotlib.pyplot as plt

# Uncomment the next line if you're using a Jupyter Notebook:
# %matplotlib inline

# Parameters and domain settings
# -------------------------------
N = 128              # Number of grid points in each direction
L = 2 * np.pi        # Domain length (periodic domain)
dx = L / N
x = np.linspace(0, L, N, endpoint=False)
y = np.linspace(0, L, N, endpoint=False)
X, Y = np.meshgrid(x, y)

# Fourier space setup
# -------------------------------
# Fourier frequencies (converted to angular wavenumbers)
kx = np.fft.fftfreq(N, d=dx) * 2 * np.pi
ky = np.fft.fftfreq(N, d=dx) * 2 * np.pi
kx, ky = np.meshgrid(kx, ky)
k2 = kx**2 + ky**2
k = np.sqrt(k2)

# Define amplitude scaling for a turbulent field
# -----------------------------------------------------
# For 3D turbulence with Kolmogorov's law:
# E(k) ~ k^(-5/3) and since in 3D E(k) ∝ k^2 |u(k)|^2,
# we choose u(k) ∝ k^(-11/6), so that:
# k^2 * (k^(-11/6))^2 = k^2 * k^(-11/3) = k^(-5/3)
# To avoid issues at k=0, compute the amplitude only for nonzero k.
amplitude = np.zeros_like(k)
nonzero = k > 0
amplitude[nonzero] = k[nonzero]**(-11/6)

# Generate a random phase field for each Fourier mode
random_phase = np.exp(1j * 2 * np.pi * np.random.rand(N, N))
base_field = amplitude * random_phase

# Construct the velocity field in Fourier space
# -----------------------------------------------
# Create two fields for the velocity components
u_hat_x = base_field.copy()
u_hat_y = base_field.copy()

# Enforce incompressibility (divergence-free condition)
# Replace zeros in k2 with 1 to avoid division by zero.
k2_nozero = np.where(k2 == 0, 1.0, k2)
divergence = (kx * u_hat_x + ky * u_hat_y) / k2_nozero

u_hat_x -= kx * divergence
u_hat_y -= ky * divergence

# Transform back to physical space
u_x = np.real(np.fft.ifft2(u_hat_x))
u_y = np.real(np.fft.ifft2(u_hat_y))

# Plot the velocity field (quiver plot)
plt.figure(figsize=(6,6))
plt.quiver(X, Y, u_x, u_y, scale=5)
plt.title("Synthetic Turbulent Velocity Field")
plt.xlabel("x")
plt.ylabel("y")
plt.tight_layout()
plt.show()

# Compute the energy spectrum
# Compute Fourier transforms of the velocity components
u_hat_x_full = np.fft.fft2(u_x)
u_hat_y_full = np.fft.fft2(u_y)
E_k = 0.5 * (np.abs(u_hat_x_full)**2 + np.abs(u_hat_y_full)**2)

# Create radial bins for averaging the energy spectrum by wavenumber magnitude
k_bins = np.linspace(0, np.max(k), 50)
E_spectrum = np.zeros(len(k_bins) - 1)
k_bin_centers = 0.5 * (k_bins[:-1] + k_bins[1:])

# Radially average the energy in Fourier space
for i in range(len(k_bins) - 1):
    mask = (k >= k_bins[i]) & (k < k_bins[i+1])
    E_spectrum[i] = E_k[mask].sum()

# Plot the energy spectrum with a reference Kolmogorov -5/3 slope
plt.figure()
plt.loglog(k_bin_centers, E_spectrum, 'o-', label="Synthetic E(k)")

# Avoid k=0 for the reference line:
mask_centers = k_bin_centers > 0
index_for_scaling = 5 if np.sum(mask_centers) > 5 else 1
ref_line = E_spectrum[mask_centers][index_for_scaling] * (k_bin_centers[mask_centers] / k_bin_centers[mask_centers][index_for_scaling])**(-5/3)
plt.loglog(k_bin_centers[mask_centers], ref_line, 'k--', label=r"Kolmogorov $k^{-5/3}$")
plt.xlabel("Wavenumber k")
plt.ylabel("E(k)")
plt.title("Energy Spectrum Comparison")
plt.legend()
plt.tight_layout()
plt.show()
