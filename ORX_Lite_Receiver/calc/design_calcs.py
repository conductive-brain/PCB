"""ORX-LITE design calculations. Every number in docs/design_process.md comes from here.

Run:  python calc/design_calcs.py      (writes calc/results.txt)

Inputs come from the datasheets (S5971 KPIN1025E, OPA365 SBOS365G, ADS7042 SBAS608C,
LP5907 SNVS798Q) or are design choices; each one says which.
"""
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
k_B, T = 1.380649e-23, 300.0          # Boltzmann constant, temperature for noise (K)
lines = []


def out(name, value, unit, note=''):
    lines.append('%-34s %12.4g %-7s %s' % (name, value, unit, note))


def head(title):
    lines.append('')
    lines.append('== ' + title)


# ---------------------------------------------------------------- inputs
V_5V = 5.0            # host USB 5 V, nominal (choice: J1 pin 1)
V_3V3A = 3.3          # U1 LP5907-3.3 output (datasheet)
V_ADC = 3.0           # U2 LP5907-3.0 output = ADC AVDD = ADC full scale (ADS7042 datasheet)
I_OPA_MAX = 5e-3      # OPA365 quiescent current, max per amplifier (datasheet)
I_AVDD = 230e-6       # ADS7042 AVDD current at 1 MSPS, 3 V (datasheet)
V_LED = 2.0           # green LED forward voltage (assumption)
S_830 = 0.60          # S5971 responsivity at 830 nm, A/W (datasheet)
C_D = 7.5e-12         # S5971 capacitance at about 2.5 V reverse bias (read from datasheet graph)
C_CM, C_DIFF = 2e-12, 6e-12   # OPA365 input capacitance (datasheet)
C_PCB = 0.5e-12       # pads and trace at the TIA input (assumption)
GBW = 50e6            # OPA365 gain-bandwidth (datasheet)
F2 = 200e6            # OPA365 second pole for the stability check (assumption)
EN = 4.5e-9           # OPA365 voltage noise at 100 kHz, V/rtHz (datasheet)
V_OUT_MIN = 0.05      # lowest TIA output we use; OPA365 reaches 20 mV max of the rail (choice)
SNR_ADC_DB = 70.0     # ADS7042 SNR at AVDD = 3 V (datasheet, typical)
C_SAMPLE = 15e-12     # ADS7042 sampling capacitor (datasheet)
T_ACQ = 200e-9        # ADS7042 minimum acquisition time (datasheet)
F_SCLK = 16e6         # ADS7042 maximum SCLK (datasheet)
FS = 1e6              # sample rate (choice)
N_BITS = 12

# component values (choices, explained in docs/design_process.md)
R1, R2 = 1e3, 1e3
C7 = 10e-6
R3, C10 = 100e3, 10e-12
R4, R5, C11 = 2e3, 10e3, 10e-6
R6 = R7 = 4.99e3
C13, C14 = 220e-12, 100e-12
R8, C16 = 22.0, 1.5e-9
R12 = 10e3

# ---------------------------------------------------------------- power
head('Power')
i_5v = 2 * I_OPA_MAX + I_AVDD + V_ADC / (R4 + R5)
out('5 V current, max', i_5v * 1e3, 'mA', '2 op amps + ADC AVDD + VREF divider')
out('U1 heat', (V_5V - V_3V3A) * 2 * I_OPA_MAX * 1e3, 'mW', '(5 - 3.3) V x 10 mA')
out('U2 heat', (V_5V - V_ADC) * (I_AVDD + V_ADC / (R4 + R5)) * 1e3, 'mW', '(5 - 3.0) V x U2 load')
out('LED current', (V_3V3A - V_LED) / R1 * 1e3, 'mA', '(3.3 - 2.0) V / R1')
out('R12 current when CS is low', 3.3 / R12 * 1e3, 'mA', '3.3 V / R12')

# ---------------------------------------------------------------- bias
head('Photodiode bias')
v_ref = V_ADC * R5 / (R4 + R5)
out('Bias filter corner', 1 / (2 * math.pi * R2 * C7), 'Hz', '1/(2 pi R2 C7)')
out('Reverse bias', V_5V - v_ref, 'V', '5 V - VREF_TIA')

# ---------------------------------------------------------------- TIA
head('TIA')
i_fs = (v_ref - V_OUT_MIN) / R3
c_in = C_D + C_CM + C_DIFF + C_PCB
out('VREF_TIA', v_ref, 'V', '3.0 V x R5/(R4+R5)')
out('Gain', R3 * 1e-6, 'V/uA', 'R3')
out('Full-scale photocurrent', i_fs * 1e6, 'uA', '(VREF - 0.05 V)/R3')
out('Full-scale light at 830 nm', i_fs / S_830 * 1e6, 'uW', 'I / 0.60 A/W')
out('TIA pole', 1 / (2 * math.pi * R3 * C10) / 1e3, 'kHz', '1/(2 pi R3 C10)')
out('Input capacitance', c_in * 1e12, 'pF', 'Cd + Ccm + Cdiff + Cpcb')
out('Noise gain at high f', 1 + c_in / C10, 'V/V', '1 + Cin/C10')
out('Smallest stable C10', math.sqrt(c_in / (2 * math.pi * R3 * GBW)) * 1e12, 'pF', 'sqrt(Cin/(2 pi R3 GBW))')
out('VREF filter corner', 1 / (2 * math.pi * (R4 * R5 / (R4 + R5)) * C11), 'Hz', '1/(2 pi (R4||R5) C11)')

f = np.logspace(2, 9, 40000)
s = 2j * np.pi * f
A = 2 * np.pi * GBW / s / (1 + s / (2 * np.pi * F2))
Zf = R3 / (1 + s * R3 * C10)
Zi = 1 / (s * c_in)
loop = A * Zi / (Zi + Zf)
H_tia = Zf * loop / (1 + loop) / R3
k = np.argmin(abs(abs(loop) - 1))
out('Loop crossover', f[k] / 1e6, 'MHz', 'model GBW/s with a 200 MHz pole')
out('Phase margin', 180 + math.degrees(np.angle(loop[k])), 'deg', '> 45 deg = stable')

# ---------------------------------------------------------------- filter
head('Sallen-Key filter and ADC input')
f0 = 1 / (2 * math.pi * R6 * math.sqrt(C13 * C14))
Q = math.sqrt(C13 * C14) / (C14 * (R6 + R7)) * math.sqrt(R6 * R7)
H_sk = 1 / (1 + s * C14 * (R6 + R7) + s ** 2 * R6 * R7 * C13 * C14)
H_rc = 1 / (1 + s * R8 * C16)
H = abs(H_tia * H_sk * H_rc)
out('Filter corner f0', f0 / 1e3, 'kHz', '1/(2 pi R sqrt(C13 C14))')
out('Filter Q', Q, '', '0.707 = flattest')
out('Chain -3 dB', f[np.argmax(H < 1 / math.sqrt(2))] / 1e3, 'kHz', 'TIA x filter x RC')
for fx in (500e3, 900e3):
    out('Chain gain at %d kHz' % (fx / 1e3), 20 * math.log10(H[np.argmin(abs(f - fx))]), 'dB', '')
out('RC corner (R8, C16)', 1 / (2 * math.pi * R8 * C16) / 1e6, 'MHz', '1/(2 pi R8 C16)')
out('C16 minimum (datasheet rule)', 20 * C_SAMPLE * 1e12, 'pF', '20 x 15 pF')
out('Op-amp GBW needed', 4 / (2 * math.pi * R8 * C16) / 1e6, 'MHz', '4/(2 pi R8 C16); OPA365 has 50')
tau = R8 * C16
T_SU = 15e-9          # CS falling to first SCLK falling, minimum (datasheet timing table)
t_conv = 12.5 / F_SCLK + T_SU
t_acq = 1 / FS - t_conv
out('Conversion time at 16 MHz', t_conv * 1e9, 'ns', '12.5 SCLK periods + 15 ns setup')
out('Acquisition time at 1 MSPS', t_acq * 1e9, 'ns', '1 us - conversion; datasheet minimum 200 ns')
out('RC time constant', tau * 1e9, 'ns', 'R8 x C16')
dip = V_ADC * C_SAMPLE / (C_SAMPLE + C16)
out('Worst sampling dip', dip * 1e3, 'mV', '3.0 V x 15 pF / (15 pF + 1.5 nF)')
out('Dip left after 200 ns', dip * math.exp(-T_ACQ / tau) * 1e6, 'uV', 'must be < half an LSB')

# ---------------------------------------------------------------- noise
head('Noise')
lsb = V_ADC / 2 ** N_BITS
v_adc = V_ADC / (2 * math.sqrt(2)) * 10 ** (-SNR_ADC_DB / 20)
e_r3 = math.sqrt(4 * k_B * T * R3)
NG = abs(1 + Zf / Zi)
n_tia = np.sqrt((e_r3 * abs(1 / (1 + s * R3 * C10))) ** 2 + (EN * NG * abs(loop / (1 + loop))) ** 2)
n_r = math.sqrt(4 * k_B * T * R6)
n_out = np.sqrt((n_tia * abs(H_sk * H_rc)) ** 2 + 2 * (n_r * abs(H_sk * H_rc)) ** 2 + (EN * abs(H_rc)) ** 2)
v_fe = math.sqrt(np.trapezoid(n_out ** 2, f))
v_tot = math.hypot(v_fe, v_adc)
out('LSB', lsb * 1e6, 'uV', '3.0 V / 4096')
out('R3 noise density', e_r3 * 1e9, 'nV/rtHz', 'sqrt(4 k T R3)')
out('Front-end noise at the ADC', v_fe * 1e6, 'uVrms', 'integrated to 1 GHz')
out('ADC noise', v_adc * 1e6, 'uVrms', 'from SNR 70 dB')
out('Total noise', v_tot * 1e6, 'uVrms', 'sqrt(front end^2 + ADC^2)')
out('Total noise in LSB', v_tot / lsb, 'LSB', '')
out('Smallest light change seen', v_tot / R3 * 1e9, 'nArms', 'total noise / R3')

text = '\n'.join(lines) + '\n'
open(os.path.join(HERE, 'results.txt'), 'w', encoding='utf-8').write(text)
print(text)
