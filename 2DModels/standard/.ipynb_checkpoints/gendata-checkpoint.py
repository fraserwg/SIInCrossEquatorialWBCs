#! /usr/bin/env python3
import mds
import numpy as np
import matplotlib.pyplot as plt
import okapy.thermo as okt
import okapy.phi as okphi
from scipy.optimize import root_scalar

# Set filenames
input_pf = './input'
precision = 'float32'

bathymetry_fn = '/bathy'
uvel_fn = '/uvel'
vvel_fn = '/vvel'
Tinit_fn = '/Tinit'
Tref_fn = '/Tref'
Sref_fn = '/Sref'
deltaZ_fn = '/deltaZ'

Tinit_ffn = input_pf + Tinit_fn
Tref_ffn = input_pf + Tref_fn
Sref_ffn = input_pf + Sref_fn
deltaZ_ffn = input_pf + deltaZ_fn
bathy_ffn = input_pf + bathymetry_fn
uvel_ffn = input_pf + uvel_fn
vvel_ffn = input_pf + vvel_fn

# Set model domain parameters
nx = 200
ny = 1
nz = 160

dx = 2e3
dy = 2e3
H = 1500

# Set the upper level spacing
dztop = 6.25 * np.ones(80)

# Set the lower level spacing
Hlower = H - dztop.sum()

def res(m, dz0=6.25, Hlower=1000):
    ''' for use when calculating lower level spacing

    Arguments:
        m --> the d(delta z)/d(model level)
        dz0 --> delta z at top of lower levels
        Hlower --> total depth of lower levels
    '''
    dzlower = m * np.arange(80) + dz0
    res = Hlower - dzlower.sum()
    return res

m = root_scalar(res, args=(6.25, Hlower), x0=0.1, x1=0.2).root
dzlower = m * np.arange(80) + 6.25

dz = np.concatenate((dztop,dzlower))

# Check the depths and spacing agree
assert dzlower.sum() == Hlower, 'Total depth in dzlower not equal to Hlower'
assert dz.sum() == H, 'Total depth in dz not equal to H'

mds.wrmds(deltaZ_ffn, dz, dataprec=precision)


Lx = nx * dx
Ly = ny * dy

# The jet parameters
V0 = 1.2
xmid = 40e3
deltab = 30e3

# Physical parameters (for thermal wind calculation)
f = 1.15e-5
g = 9.81

# Thermodynamic parameters
S = 48

# Bathymetry
h = -1 * H * np.ones((ny, nx))
h[:, (0, -1)] = 0  # Add wall along nx = (0, -1)
mds.wrmds(bathy_ffn, h, dataprec=precision)

# Make grids
x1 = np.linspace(0, Lx, nx)
xnz = np.repeat(x1[np.newaxis, :], nz, axis=0)

z1 = np.cumsum(dz)
znx = np.repeat(z1[:, np.newaxis], nx, axis=1)

# Uvel
Uinit = np.zeros((nz, ny, nx))
mds.wrmds(uvel_ffn, Uinit, dataprec=precision)

# Vvel
Vinit = V0 * (1 - np.square(np.tanh((xnz - xmid) / deltab))) * (-znx + H) / H
mds.wrmds(vvel_ffn, Vinit, dataprec=precision)

# Plot the Vvel
plt.figure()
plt.pcolormesh(xnz*1e-3, -znx, Vinit, cmap='Reds')
plt.colorbar().set_label('V (ms$^{-1}$)')
plt.xlabel('Longitude (km)')
plt.ylabel('Depth (m)')
plt.title('Meridional Velocity')
plt.show()

# Thermal wind - assume rho(x, z) = phi(z) * chi(x)
# chi(x) part can be calculated analytically from thermal wind

def chi_x(x):
    tanh_part1 = np.tanh((xmid - x) / deltab)
    tanh_part2 = np.tanh((xmid - Lx) / deltab)
    tanh_term = V0 * f / g / H * deltab * (tanh_part1 - tanh_part2)
    chi_field = np.exp(tanh_term)
    return chi_field

# phi(z) can be taken from a suitable argo profile
# A function in okapy will do this for us
phi_z = okphi.generate_phi_z()

# Create the Tref and Tinit profiles (S is fixed)
Tref = okt.T_from_rho(phi_z(z1), S)
Sref = S * np.ones(nz)
mds.wrmds(Tref_ffn, Tref, dataprec=precision)
mds.wrmds(Sref_ffn, Sref, dataprec=precision)

rho_init = phi_z(znx) * chi_x(xnz)
Tinit = okt.T_from_rho(rho_init, S)
mds.wrmds(Tinit_ffn, Tinit, dataprec=precision)
