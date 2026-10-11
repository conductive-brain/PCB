# Design process

How ORX-LITE was designed: from what it must do, to every value on the schematic.
Every number comes from `calc/design_calcs.py` (output in `calc/results.txt`), unless it says
"datasheet" or "choice". Each formula has its LibreOffice StarMath code under it.

## 1. What the board must do

| Need | Value | Source |
|---|---|---|
| Light input | one photodiode, 320 to 1060 nm | choice; S5971 datasheet |
| Signal speed | about 100 kHz | choice |
| Sampling | 12 bits, 1 million samples per second | choice |
| Interface | SPI, 3 wires, 3.3 V logic, to any microcontroller board | choice |
| Power | 5 V and 3.3 V from the microcontroller board | choice |
| Board | 4 layers, about 50 x 40 mm | choice |

## 2. The chain

```
light → photodiode → TIA → low-pass filter → R8 + C16 → ADC → J1 → microcontroller
        (current)    (voltage)  (clean voltage)            (numbers)
```

- The photodiode makes a current that follows the light.
- The TIA turns the current into a voltage.
- The filter removes everything faster than the ADC can handle.
- R8 and C16 feed the ADC's sampling capacitor.
- The ADC turns the voltage into numbers and sends them over SPI.

## 3. Power

```
J1 5 V   → FB1 → +5V_F → U1 → +3V3_A   → op amps U3, U4
                       → U2 → +3V0_ADC → ADC supply and reference, VREF divider
                       → R2 → PD_K     → photodiode bias
J1 3.3 V → FB2 → +3V3_D → ADC digital side, LED, CS pull-up
```

**Why linear regulators.** A switching regulator makes ripple at its switching frequency, right
where our signal lives. A linear regulator makes no ripple; it only turns the extra voltage into heat.

**Why two regulators.** The ADC uses its supply as its reference, so it gets a quiet supply of its own.
This also keeps the ADC's current pulses off the op amps' supply.

**How much current we take from 5 V** (op amps 5 mA max each, datasheet; ADC 0.23 mA, datasheet;
VREF divider 3.0 V / 12 kΩ):

$$I_{5V} = 2 \cdot 5\,\text{mA} + 0.23\,\text{mA} + \frac{3.0\,\text{V}}{12\,\text{k}\Omega} = 10.5\,\text{mA}$$

```
I_{5V} = 2 cdot 5 " mA" + 0.23 " mA" + {3.0 " V"} over {12 " k" %OMEGA} = 10.5 " mA"
```

**How hot U1 gets.** Small, so no cooling needed:

$$P_{U1} = (5.0 - 3.3)\,\text{V} \times 10\,\text{mA} = 17\,\text{mW}$$

```
P_{U1} = (5.0 - 3.3) " V" times 10 " mA" = 17 " mW"
```

**LED current** (2.0 V green LED drop is an assumption):

$$I_{LED} = \frac{3.3\,\text{V} - 2.0\,\text{V}}{1\,\text{k}\Omega} = 1.3\,\text{mA}$$

```
I_{LED} = {3.3 " V" - 2.0 " V"} over {1 " k" %OMEGA} = 1.3 " mA"
```

## 4. Photodiode bias

A photodiode with a positive voltage on its cathode (reverse bias) is faster and more linear.
Our only voltage above 3.3 V is the 5 V from the host, so the cathode gets filtered 5 V.

$$f_{bias} = \frac{1}{2\pi R_2 C_7} = \frac{1}{2\pi \cdot 1\,\text{k}\Omega \cdot 10\,\mu\text{F}} = 16\,\text{Hz}$$

```
f_{bias} = 1 over {2 %pi R_2 C_7} = 1 over {2 %pi cdot 1 " k" %OMEGA cdot 10 " %mu F"} = 16 " Hz"
```

The anode sits at VREF_TIA = 2.5 V (section 5), so:

$$V_{bias} = 5.0\,\text{V} - 2.5\,\text{V} = 2.5\,\text{V}$$

```
V_{bias} = 5.0 " V" - 2.5 " V" = 2.5 " V"
```

At 2.5 V the S5971 has about 7.5 pF (read from the datasheet graph). At 10 V it would have 3 pF.
For a 100 kHz signal, 7.5 pF is fine.

## 5. TIA: current to voltage

The op amp keeps its − input at the same voltage as its + input (2.5 V). The photocurrent cannot
flow into the op amp's input (only 0.2 pA flows there, datasheet). So all of it flows through R3:

$$V_{TIA} = V_{REF} - I_{ph} \cdot R_3$$

```
V_{TIA} = V_{REF} - I_{ph} cdot R_3
```

Examples: no light gives 2.5 V. 10 µA gives 2.5 V − 10 µA × 100 kΩ = 1.5 V.

**The 2.5 V reference.** The output can only go down with light, so it starts high:

$$V_{REF} = 3.0\,\text{V} \cdot \frac{R_5}{R_4 + R_5} = 3.0\,\text{V} \cdot \frac{10\,\text{k}}{12\,\text{k}} = 2.5\,\text{V}$$

```
V_{REF} = 3.0 " V" cdot {R_5} over {R_4 + R_5} = 3.0 " V" cdot {10 " k"} over {12 " k"} = 2.5 " V"
```

It comes from +3V0_ADC, the ADC's own reference. If that rail is 2 % high, VREF and the ADC's range
are both 2 % high, and the dark reading stays the same (a "ratiometric" design).
C11 filters the reference:

$$f_{ref} = \frac{1}{2\pi \frac{R_4 R_5}{R_4 + R_5} C_{11}} = \frac{1}{2\pi \cdot 1.67\,\text{k}\Omega \cdot 10\,\mu\text{F}} = 9.5\,\text{Hz}$$

```
f_{ref} = 1 over {2 %pi {R_4 R_5} over {R_4 + R_5} C_{11}} = 1 over {2 %pi cdot 1.67 " k" %OMEGA cdot 10 " %mu F"} = 9.5 " Hz"
```

**Choosing R3 (the gain).** The output can go from 2.5 V down to about 0.05 V (the OPA365 gets
within 20 mV of its rail, datasheet; 0.05 V is our margin). R3 = 100 kΩ gives:

$$I_{FS} = \frac{V_{REF} - 0.05\,\text{V}}{R_3} = \frac{2.45\,\text{V}}{100\,\text{k}\Omega} = 24.5\,\mu\text{A}$$

```
I_{FS} = {V_{REF} - 0.05 " V"} over R_3 = {2.45 " V"} over {100 " k" %OMEGA} = 24.5 " %mu A"
```

$$P_{FS} = \frac{I_{FS}}{0.60\,\text{A/W}} = 41\,\mu\text{W at 830 nm}$$

```
P_{FS} = I_{FS} over {0.60 " A/W"} = 41 " %mu W"
```

A bigger R3 would see weaker light but would run out of range sooner and be slower.

**Choosing C10 (the speed).** C10 and R3 set the TIA's bandwidth:

$$f_p = \frac{1}{2\pi R_3 C_{10}} = \frac{1}{2\pi \cdot 100\,\text{k}\Omega \cdot 10\,\text{pF}} = 159\,\text{kHz}$$

```
f_p = 1 over {2 %pi R_3 C_{10}} = 1 over {2 %pi cdot 100 " k" %OMEGA cdot 10 " pF"} = 159 " kHz"
```

C10 also keeps the TIA stable. The capacitance at the − input (photodiode, op-amp input, pads)
can make the amplifier ring. That capacitance is:

$$C_{in} = C_d + C_{cm} + C_{diff} + C_{pcb} = 7.5 + 2 + 6 + 0.5 = 16\,\text{pF}$$

```
C_{in} = C_d + C_{cm} + C_{diff} + C_{pcb} = 7.5 + 2 + 6 + 0.5 = 16 " pF"
```

(op-amp input capacitance: datasheet; 0.5 pF for pads: assumption). The smallest C10 that keeps
the TIA stable is:

$$C_{10,min} = \sqrt{\frac{C_{in}}{2\pi R_3 \cdot GBW}} = \sqrt{\frac{16\,\text{pF}}{2\pi \cdot 100\,\text{k}\Omega \cdot 50\,\text{MHz}}} = 0.71\,\text{pF}$$

```
C_{10,min} = sqrt{ C_{in} over {2 %pi R_3 cdot GBW} } = sqrt{ {16 " pF"} over {2 %pi cdot 100 " k" %OMEGA cdot 50 " MHz"} } = 0.71 " pF"
```

10 pF is far above that: the phase margin is 84° (model; above 45° counts as stable). We use the
larger value on purpose: it limits the bandwidth to what we need, and less bandwidth means less noise.

## 6. Low-pass filter

The ADC samples 1 million times per second. Anything faster than half of that (500 kHz) folds back
and looks like a slow signal. This is called aliasing. The filter removes it before the ADC sees it.

The filter is a 2nd-order Sallen-Key with R6 = R7 = R:

$$f_0 = \frac{1}{2\pi R \sqrt{C_{13} C_{14}}} = \frac{1}{2\pi \cdot 4.99\,\text{k}\Omega \cdot \sqrt{220\,\text{pF} \cdot 100\,\text{pF}}} = 215\,\text{kHz}$$

```
f_0 = 1 over {2 %pi R sqrt{C_{13} C_{14}}} = 1 over {2 %pi cdot 4.99 " k" %OMEGA cdot sqrt{220 " pF" cdot 100 " pF"}} = 215 " kHz"
```

$$Q = \frac{1}{2}\sqrt{\frac{C_{13}}{C_{14}}} = \frac{1}{2}\sqrt{\frac{220}{100}} = 0.74$$

```
Q = 1 over 2 sqrt{ C_{13} over C_{14} } = 1 over 2 sqrt{ 220 over 100 } = 0.74
```

Q = 0.707 is the flattest response; 0.74 is within 0.04 dB of flat. We use E12 values (220 pF, 100 pF).

**The whole chain** (TIA, filter, R8 + C16) is flat up to 143 kHz (−3 dB). It is 25 dB down at
500 kHz and 40 dB down at 900 kHz, where signals would fold back into our band.

## 7. Feeding the ADC: R8 and C16

At each sample the ADC connects its 15 pF capacitor (datasheet) to the input. That capacitor takes
some charge and makes a small dip. C16 supplies the charge. The datasheet's rule:

$$C_{16} \ge 20 \cdot C_{sample} = 20 \cdot 15\,\text{pF} = 300\,\text{pF} \quad \Rightarrow \quad 1.5\,\text{nF}$$

```
C_{16} >= 20 cdot C_{sample} = 20 cdot 15 " pF" = 300 " pF"
```

R8 keeps U4 from ringing while it drives C16. The datasheet asks for an op amp fast enough:

$$GBW \ge \frac{4}{2\pi R_8 C_{16}} = \frac{4}{2\pi \cdot 22\,\Omega \cdot 1.5\,\text{nF}} = 19\,\text{MHz}$$

```
GBW >= 4 over {2 %pi R_8 C_{16}} = 4 over {2 %pi cdot 22 %OMEGA cdot 1.5 " nF"} = 19 " MHz"
```

The OPA365 has 50 MHz. TI's own example uses 25 Ω and 1.5 nF.

**Does the dip recover in time?** At 1 MSPS with a 16 MHz clock, the ADC converts for
12.5 clock periods plus 15 ns of setup (datasheet). The time left to take the next sample is:

$$t_{acq} = 1\,\mu\text{s} - (12.5 \cdot 62.5\,\text{ns} + 15\,\text{ns}) = 204\,\text{ns}$$

```
t_{acq} = 1 " %mu s" - (12.5 cdot 62.5 " ns" + 15 " ns") = 204 " ns"
```

The datasheet needs at least 200 ns, so 1 MSPS just fits. The worst dip and what is left of it after
200 ns (R8 × C16 = 33 ns):

$$\Delta V = 3.0\,\text{V} \cdot \frac{15\,\text{pF}}{15\,\text{pF} + 1.5\,\text{nF}} = 29.7\,\text{mV}, \qquad \Delta V \cdot e^{-200\,\text{ns}/33\,\text{ns}} = 69\,\mu\text{V}$$

```
%DELTA V = 3.0 " V" cdot {15 " pF"} over {15 " pF" + 1.5 " nF"} = 29.7 " mV" ~~~~ %DELTA V cdot e^{-200 " ns" / 33 " ns"} = 69 " %mu V"
```

69 µV is below half an LSB (366 µV). This simple estimate assumes U4's output is stiff;
the SPICE simulation (step 5) checks it with the real op amp.

## 8. ADC and SPI

- **Input:** AINM to GND, AINP to ADC_IN. The ADC reads 0 to 3.0 V as 0 to 4095.
- **One step (LSB):**

$$LSB = \frac{3.0\,\text{V}}{4096} = 732\,\mu\text{V}$$

```
LSB = {3.0 " V"} over 4096 = 732 " %mu V"
```

- **A frame:** CS goes low, the ADC needs 14 SCLK cycles: two zeros, then 12 data bits, MSB first.
  The first frame after power-up is an offset calibration: hold CS low for at least 16 SCLKs
  (datasheet).
- **33 Ω on SCLK, CS_N, SDO:** fast edges ring on the wires to the host. A small resistor at the end
  that drives each wire softens the edge.
- **R12, 10 kΩ pull-up on CS:** keeps the ADC idle until the host drives CS.
  Costs 0.33 mA while CS is low.

## 9. Noise: how small a light change we can see

The ADC's own noise follows from its SNR (70 dB at 3.0 V, datasheet):

$$v_{ADC} = \frac{3.0\,\text{V}}{2\sqrt{2}} \cdot 10^{-70/20} = 335\,\mu\text{V}_{rms}$$

```
v_{ADC} = {3.0 " V"} over {2 sqrt 2} cdot 10^{-70/20} = 335 " %mu V"_{rms}
```

The front end (R3's noise, op-amp noise, filter resistors) adds 22 µVrms at the ADC input (calc, integrated
to 1 GHz). R3's own noise density is:

$$e_{R3} = \sqrt{4 k T R_3} = 40.7\,\text{nV}/\sqrt{\text{Hz}}$$

```
e_{R3} = sqrt{4 k T R_3} = 40.7 " nV/" sqrt{"Hz"}
```

Noises add as a root sum of squares:

$$v_{tot} = \sqrt{v_{front}^2 + v_{ADC}^2} = \sqrt{22^2 + 335^2}\,\mu\text{V} = 336\,\mu\text{V}_{rms} = 0.46\,\text{LSB}$$

```
v_{tot} = sqrt{v_{front}^2 + v_{ADC}^2} = sqrt{22^2 + 335^2} " %mu V" = 336 " %mu V"_{rms}
```

The ADC sets the noise floor; the front end barely adds to it. Referred back to the light current:

$$i_{min} = \frac{v_{tot}}{R_3} = \frac{336\,\mu\text{V}}{100\,\text{k}\Omega} = 3.4\,\text{nA}_{rms}$$

```
i_{min} = v_{tot} over R_3 = {336 " %mu V"} over {100 " k" %OMEGA} = 3.4 " nA"_{rms}
```

## 10. Still to check

- SPICE simulation of the chain: frequency response, noise, and the dip at the ADC input (step 5).
- Layout rules, from placement to routing (steps 7 and 8).
