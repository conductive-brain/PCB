# Components

Every part on ORX-LITE: what it is, why it is there, how it is connected, and where it came from.

## How the parts were found

Every part started from a need written as numbers, for example "3.3 V from 5 V, about 10 mA,
low noise". The first candidate for each need came from the TI and Hamamatsu catalogues.
Then the datasheet confirmed every number used here.

To repeat a search yourself:
1. Open the manufacturer's selection table (on ti.com: pick the product type, then set the filters)
   or a distributor (LCSC, Digi-Key, Mouser).
2. Filter by the numbers in your need. Sort by what matters most: noise, price, stock.
3. Read the datasheet of the best 2 or 3: limits, electrical table, pinout, example circuit.
4. Check that KiCad has the symbol and footprint, and that the pin numbers match the datasheet.

Datasheets used: LP5907 (TI SNVS798Q), OPA365 (TI SBOS365G), ADS7042 (TI SBAS608C),
S5971 (Hamamatsu KPIN1025E).

## All parts at a glance

| Ref | Part | Job |
|---|---|---|
| J1 | 2x5 pin header | power in, SPI out |
| FB1, FB2 | ferrite beads | block noise from the host |
| C1, C6 | 10 µF | hold the filtered supplies steady |
| U1 | LP5907 3.3 V regulator | quiet supply for the op amps |
| U2 | LP5907 3.0 V regulator | supply and reference for the ADC |
| C2 to C5 | 1 µF | regulator input and output capacitors |
| D1, R1 | LED, 1 kΩ | power-on light |
| TP1 to TP8 | test points | places to measure |
| R2, C7, C8 | 1 kΩ, 10 µF, 100 nF | clean bias for the photodiode |
| D2 | S5971 photodiode | turns light into current |
| U3 | OPA365 | TIA: current to voltage |
| R3, C10 | 100 kΩ, 10 pF | TIA gain and bandwidth |
| R4, R5, C11, C12 | 2 kΩ, 10 kΩ, 10 µF, 100 nF | 2.5 V reference for the TIA |
| C9, C15 | 100 nF | op-amp supply decoupling |
| U4 | OPA365 | low-pass filter, drives the ADC |
| R6, R7, C13, C14 | 4.99 kΩ, 4.99 kΩ, 220 pF, 100 pF | filter parts |
| R8, C16 | 22 Ω, 1.5 nF | ADC input network |
| U5 | ADS7042 | 12-bit ADC with SPI |
| C17, C18 | 1 µF | ADC supply decoupling |
| R9, R10, R11 | 33 Ω | soften the SPI edges |
| R12 | 10 kΩ | keeps the ADC idle at start-up |
| H1 to H4 | M3 holes | mounting |

---

## Power

### J1: 2x5 pin header, 2.54 mm pitch
- **What:** two rows of 5 pins. Jumper wires or a ribbon cable plug onto it.
- **Why:** the board gets its power from the microcontroller board and sends it the data.
- **How we use it:** pin 1 = 5 V, pin 3 = 3.3 V, pin 5 = SCLK, pin 7 = CS_N, pin 9 = SDO.
  All even pins are GND, so every wire has its own ground wire next to it. That keeps the
  signal and its return path together and stops ringing on SCLK.
- **Where we found it:** a standard part from any maker (KiCad: `Conn_02x05_Odd_Even`).
- **Footprint:** `PinHeader_2x05_P2.54mm_Vertical`.

### FB1, FB2: ferrite beads, 220 Ω at 100 MHz, 0603
- **What:** a small part that acts like a wire for DC and like a resistor for fast noise.
- **Why:** the host's USB 5 V and 3.3 V carry noise from its digital circuits.
- **How we use it:** in series with the supply: J1 5 V → FB1 → +5V_F, and J1 3.3 V → FB2 → +3V3_D.
  With the capacitor after it, it forms a low-pass filter.
- **Where we found it:** Murata BLM18 series, a common choice at any distributor. Search: ferrite bead,
  0603, 120 to 600 Ω at 100 MHz, rated above 200 mA. Part number BLM18PG221SN1D is from memory:
  check it at a distributor before ordering.
- **Footprint:** `L_0603_1608Metric`.

### C1, C6: 10 µF, 10 V, X5R or X7R, 0805
- **What:** ceramic capacitors that store charge.
- **Why:** they hold +5V_F and +3V3_D steady and complete the bead's filter.
- **How we use it:** from +5V_F to GND (C1) and from +3V3_D to GND (C6).
- **Why 10 V and 0805:** a ceramic capacitor loses capacitance when DC voltage is across it.
  A higher voltage rating and a bigger body lose less.
- **Footprint:** `C_0805_2012Metric`.

### U1: LP5907MFX-3.3, low-noise regulator (TI)
- **What:** a linear regulator (LDO). It turns 5 V into a steady, quiet 3.3 V.
- **Why:** the op amps need a clean supply; noise on it leaks into the signal.
  A switching regulator would add ripple, so we use a linear one. It wastes only
  (5 − 3.3) V × 10 mA = 17 mW as heat.
- **How we use it:** IN and EN to +5V_F, GND to GND, OUT gives +3V3_A.
  EN has a built-in pull-down: left open, the regulator stays off. Tied to IN, it turns on with 5 V.
- **Key numbers (datasheet):** noise below 6.5 µVrms, 82 dB supply rejection at 1 kHz,
  input 2.2 to 5.5 V, up to 250 mA, stable with 1 µF ceramic capacitors.
- **Where we found it:** ti.com, linear regulator selection table. Filters: input up to 5.5 V,
  at least 50 mA, fixed 3.3 V, noise below 10 µVrms, SOT-23-5.
  The datasheet names the newer TPS7A20 as an alternative.
- **Footprint:** `SOT-23-5`.

### U2: LP5907MFX-3.0
- **What:** the same regulator with a 3.0 V output.
- **Why:** the ADC has no separate reference pin. Its supply (AVDD) is its reference: the input range
  is 0 to AVDD. Noise on AVDD lands in every reading, so the ADC gets its own quiet regulator.
  The ADC datasheet recommends exactly this.
- **Why 3.0 V and not 3.3 V:** the op amps run on 3.3 V and can drive 0 to 3.0 V with room to spare.
  The ADC's datasheet SNR (70 dB) is given at 3.0 V.
- **How we use it:** like U1, OUT gives +3V0_ADC.
- **Footprint:** `SOT-23-5`.

### C2, C3, C4, C5: 1 µF, 0603
- **Why:** the LP5907 datasheet asks for 1 µF at the input and at least 1 µF at the output.
- **How we use it:** C2 at U1's input, C3 at U1's output, C4 at U2's input, C5 at U2's output, all to GND.

### D1 + R1: green LED + 1 kΩ, 0603
- **Why:** a light that shows the host's 3.3 V has arrived.
- **How we use it:** +3V3_D → R1 → LED anode; LED cathode → GND.
  Current = (3.3 − 2.0) V / 1 kΩ = 1.3 mA (2.0 V is a typical green LED drop; check your LED).
- **Footprints:** `LED_0603_1608Metric`, `R_0603_1608Metric`.

### TP1 to TP8: test points
- **What:** round copper pads for a probe.
- **How we use it:** TP1 +5V_F, TP2 +3V3_A, TP3 +3V0_ADC, TP4 +3V3_D, TP5 GND,
  TP6 VREF_TIA, TP7 TIA_OUT, TP8 ADC_IN.
- **Footprint:** `TestPoint_Pad_D1.0mm`.

### PWR_FLAG (not a part)
- **What:** a schematic-only symbol. No footprint, nothing on the board.
- **Why:** KiCad's electrical check wants every supply pin to have a visible source.
  Power that comes in through J1 or through a ferrite bead is invisible to it.
  The flag says "this net has a source".
- **Where:** on +5V, +3V3 and GND (from J1), on +5V_F (after FB1) and on +3V3_D (after FB2).

---

## Front end

### R2, C7, C8: photodiode bias filter (1 kΩ, 10 µF 0805, 100 nF)
- **Why:** the photodiode works better with a positive voltage on its cathode (reverse bias):
  it gets faster and more linear. The voltage must be clean, because noise on it goes
  straight into the amplifier.
- **How we use it:** +5V_F → R2 → PD_K; C7 and C8 from PD_K to GND. Low-pass at 16 Hz.
  C8 covers the very high frequencies where a big capacitor stops working well.

### D2: Hamamatsu S5971, silicon PIN photodiode
- **What:** turns light into current: 0.60 A per W at 830 nm.
- **Why:** fast (100 MHz at 10 V), small (1.2 mm), low capacitance, sees 320 to 1060 nm,
  metal can with legs that can sit at the board edge.
- **How we use it:** cathode (pin 1) to PD_K, anode (pin 3) to TIA_IN, case (pin 2) to GND.
  At our 2.5 V bias it has about 7.5 pF (read from the datasheet graph).
- **Where we found it:** Hamamatsu's Si PIN photodiode catalogue (hamamatsu.com).
  Filters: cutoff at least 10 MHz, area about 1 mm², metal can.
- **Footprint:** `TO-18-3`.

### U3: OPA365, the TIA (TI)
- **What:** an op amp used as a transimpedance amplifier: current in, voltage out.
- **Why this op amp:** works from one 3.3 V supply with inputs and output reaching both rails;
  input current only 0.2 pA (the photocurrent must not leak into it); low noise (4.5 nV/√Hz);
  fast enough (50 MHz); stable driving capacitors. One part type for both op amps.
- **How we use it:** − input to TIA_IN, + input to VREF_TIA, output to TIA_OUT,
  V+ to +3V3_A, V− to GND.
- **Where we found it:** ti.com, op-amp selection table. Filters: rail-to-rail in and out,
  2.2 to 5.5 V, at least 20 MHz, noise below 10 nV/√Hz, input current below 10 pA, SOT-23-5.
- **Footprint:** `SOT-23-5`.

### R3: 100 kΩ, and C10: 10 pF C0G
- **What:** the TIA's feedback parts, both from TIA_IN to TIA_OUT.
- **Why R3:** it sets the gain: 1 µA of light current makes 0.1 V.
- **Why C10:** it sets the bandwidth (159 kHz) and keeps the amplifier from ringing.

### R4: 2 kΩ, R5: 10 kΩ, C11: 10 µF, C12: 100 nF
- **What:** a divider that makes VREF_TIA = 2.5 V, with a filter.
- **Why:** the TIA output starts at 2.5 V with no light and goes down with light.
  VREF comes from +3V0_ADC so it moves together with the ADC's reference.
- **How we use it:** +3V0_ADC → R4 → VREF_TIA → R5 → GND; C11 and C12 from VREF_TIA to GND.

### C9, C15: 100 nF
- **Why:** a small charge store next to each op amp's supply pin. It feeds sudden current
  needs at once.
- **How we use it:** from +3V3_A to GND, right next to U3 (C9) and U4 (C15).

### U4: OPA365, the filter
- **What:** the same op amp, used as a 2nd-order low-pass filter (Sallen-Key) and as the ADC driver.
- **Why:** the ADC samples 1 million times per second. Anything faster than 500 kHz would fold
  back and look like a slow signal. The filter removes it first.
- **How we use it:** + input to SK_B, − input wired to the output, output is FLT_OUT.

### R6, R7: 4.99 kΩ, C13: 220 pF C0G, C14: 100 pF C0G
- **How we use it:** TIA_OUT → R6 → SK_A → R7 → SK_B → U4 + input.
  C13 from SK_A to FLT_OUT. C14 from SK_B to GND.
- **Why these values:** corner at 215 kHz with a flat response. C13 ≈ 2 × C14 gives the flat shape.

### R8: 22 Ω, C16: 1.5 nF C0G
- **What:** the network between the filter and the ADC.
- **Why C16:** at each sample the ADC connects its 15 pF capacitor to the input. C16 is 100
  times bigger, so it feeds that charge with almost no dip.
- **Why R8:** it stops U4 from ringing while it drives the big capacitor.
- **How we use it:** FLT_OUT → R8 → ADC_IN; C16 from ADC_IN to GND.

---

## ADC and SPI

### U5: ADS7042, 12-bit ADC (TI)
- **What:** turns a voltage into a 12-bit number, up to 1 million times per second.
- **Why:** only three SPI wires (CS, SCLK, SDO), nothing to configure, 70 dB signal-to-noise,
  one supply up to 3.6 V.
- **How we use it:** AINP (pin 6) to ADC_IN, AINM (pin 5) to GND, AVDD (pin 7) to +3V0_ADC,
  DVDD (pin 1) to +3V3_D, GND (pin 8) to GND, SCLK pin 2, SDO pin 3, CS pin 4.
- **Where we found it:** ti.com, precision ADC selection table. Filters: 12 bit, at least 1 MSPS,
  1 channel, SPI, supply below 3.6 V, leaded package.
- **Footprint:** `VSSOP-8_2.3x2mm_P0.5mm`.

### C17, C18: 1 µF
- **Why:** the datasheet asks for 1 µF on each supply pin.
- **How we use it:** C17 from AVDD to GND, C18 from DVDD to GND, both right at the pins.

### R9, R10, R11: 33 Ω
- **Why:** fast logic edges ring on wires. A small resistor at the end that drives the wire
  softens the edge and absorbs the echo.
- **How we use it:** SCLK → R10 → ADC_SCLK and CS_N → R11 → ADC_CS_N (next to J1, because the
  host drives these); ADC_SDO → R9 → SDO (next to U5, because the ADC drives it).

### R12: 10 kΩ pull-up
- **Why:** CS low means "ADC, start". While the host is not driving the line yet, R12 holds it
  high, so the ADC stays idle.
- **How we use it:** from ADC_CS_N to +3V3_D.

### H1 to H4: M3 mounting holes
- **What:** 3.2 mm holes for M3 screws or standoffs. Not parts, just holes in the board.
- **Footprint:** `MountingHole_3.2mm_M3`.
