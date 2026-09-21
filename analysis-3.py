"""
SOEC Polarization Curve Digitization and Loss Analysis
Author: Benyamin Mohammadzadeh Madiyeh

Data source: Digitized from Figure S5 (Ebbesen & Mogensen, 2009 dataset,
850C, 50% H2O) in the supplementary material of:
Estrada, N.G.A. & Cervera, R.B.M. (2025). Machine Learning-Based Predictive
Modelling for Solid Oxide Electrolysis Cell's (SOEC) Electrochemical
Performance. Applied Sciences, 15(17), 9388.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Load data ---
df = pd.read_csv('sofc_data_ebbesen2009.csv')
print(df.head())
print("Shape:", df.shape)

I = -df['current_density_A_cm2'].values  # current density magnitude (A/cm^2)
V = df['voltage_V'].values               # cell voltage (V)

# --- Plot 1: raw polarization curve ---
plt.figure(figsize=(7, 5))
plt.plot(df['current_density_A_cm2'], V, 'o-', color='darkmagenta')
plt.xlabel('Current Density (A/cm^2)')
plt.ylabel('Voltage (V)')
plt.title('SOEC Voltage-Current Curve (850C, 50% H2O)\nSource: Ebbesen & Mogensen, 2009')
plt.grid(alpha=0.3)
plt.savefig('polarization_curve.png', dpi=150, bbox_inches='tight')

# --- Loss (overpotential) separation ---
# Linear (ohmic) fit: V = V0 + ASR * I
slope, intercept = np.polyfit(I, V, 1)
V_ohmic_fit = slope * I + intercept
residuals = V - V_ohmic_fit  # non-ohmic (activation + concentration) overpotential

ss_res = np.sum(residuals**2)
ss_tot = np.sum((V - np.mean(V))**2)
r2 = 1 - ss_res / ss_tot

print(f"\nLinear fit: V = {intercept:.3f} + {slope:.3f} * I")
print(f"Apparent ASR = {slope:.3f} ohm.cm^2, R^2 = {r2:.4f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
ax1.plot(I, V, 'o', color='darkmagenta', label='Digitized data')
ax1.plot(I, V_ohmic_fit, '--', color='gray', label=f'Ohmic fit (ASR={slope:.3f} ohm.cm2)')
ax1.set_xlabel('Current Density |I| (A/cm^2)')
ax1.set_ylabel('Voltage (V)')
ax1.set_title('SOEC Voltage vs Current\n(Ebbesen & Mogensen, 2009, 850C)')
ax1.legend()
ax1.grid(alpha=0.3)

ax2.plot(I, residuals * 1000, 'o-', color='darkorange')
ax2.axhline(0, color='gray', linewidth=0.8)
ax2.set_xlabel('Current Density |I| (A/cm^2)')
ax2.set_ylabel('Non-ohmic overpotential (mV)')
ax2.set_title('Residual after removing ohmic term\n(activation + concentration contribution)')
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('loss_separation.png', dpi=150, bbox_inches='tight')
print("\nFigures saved: polarization_curve.png, loss_separation.png")

# --- Extended analysis: temperature dependence (Sun et al., 2013) ---
df2 = pd.read_csv('sun2013_multi_temp.csv')

results = {}
plt.figure(figsize=(13, 5))
ax1 = plt.subplot(1, 2, 1)
colors = {750: 'red', 800: 'purple', 850: 'green'}
for T in [750, 800, 850]:
    sub = df2[df2['temperature_C'] == T]
    I2 = -sub['current_density_A_cm2'].values
    V2 = sub['voltage_V'].values
    slope, intercept = np.polyfit(I2, V2, 1)
    results[T] = slope
    ax1.plot(I2, V2, 'o', color=colors[T], label=f'{T}C (ASR={slope:.3f} ohm.cm2)')
    ax1.plot(I2, slope * I2 + intercept, '--', color=colors[T], alpha=0.5)
ax1.set_xlabel('Current Density |I| (A/cm^2)')
ax1.set_ylabel('Voltage (V)')
ax1.set_title('SOEC Voltage-Current at 3 Temperatures\n(Sun et al., 2013)')
ax1.legend()
ax1.grid(alpha=0.3)

# Arrhenius analysis: ln(1/ASR) vs 1/T
R_gas = 8.314  # J/mol/K
T_K = np.array([T + 273.15 for T in results.keys()])
ASR = np.array(list(results.values()))
x_arr = 1 / T_K
y_arr = np.log(1 / ASR)
slope_arr, intercept_arr = np.polyfit(x_arr, y_arr, 1)
Ea = -slope_arr * R_gas / 1000  # kJ/mol

ax2 = plt.subplot(1, 2, 2)
ax2.plot(x_arr, y_arr, 'o', color='darkblue', markersize=10)
ax2.plot(x_arr, slope_arr * x_arr + intercept_arr, '--', color='gray', label=f'Ea = {Ea:.1f} kJ/mol')
ax2.set_xlabel('1/T (K^-1)')
ax2.set_ylabel('ln(1/ASR)')
ax2.set_title('Arrhenius Plot: Temperature Dependence\nof Area-Specific Resistance')
ax2.legend()
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('temperature_analysis.png', dpi=150, bbox_inches='tight')
print(f"\nActivation energy Ea = {Ea:.1f} kJ/mol")
