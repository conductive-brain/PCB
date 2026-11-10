# ORX-LITE: one-channel optical receiver

A 4-layer board that measures light. A photodiode turns light into a small current, two op amps
turn the current into a clean voltage, and a 12-bit ADC sends it as numbers, 1 million per second,
over SPI to a 3.3 V microcontroller board (for example a Raspberry Pi Pico).

```
light → S5971 photodiode → OPA365 TIA (current to voltage) → OPA365 low-pass filter
      → 22 Ω + 1.5 nF → ADS7042 ADC (12 bit, 1 MSPS) → 2x5 header → microcontroller
```

Power comes from the microcontroller board: 5 V and 3.3 V through the header.

I drew this board by hand in KiCad 9, one step at a time. Each step is one commit, and each
commit message says what was added and why.

**Status:** revision A is designed and its fabrication files are ready. It has not been ordered,
built or tested yet.

## Files

```
docs/components.md       every part: what it is, why, how it is connected, where it came from
docs/design_process.md   the whole design: needs, formulas, values, reasoning
docs/figures/            simulation plots
calc/design_calcs.py     every number in design_process.md (writes calc/results.txt)
hardware/                the KiCad project
ORX_LITE_sim/            the SPICE simulation of the front end (KiCad 9, ngspice)
release/rev-A/           files to make revision A: Gerbers and drill files (gerbers/), parts
                         list and placement file (assembly/), schematic PDF, assembly
                         drawing and 3D picture (docs/), fabrication notes (README.md)
```

## Steps

| Step | What | State |
|---|---|---|
| 1 | KiCad project, page setup | done |
| 2 | power section: J1, ferrite beads, regulators U1 and U2, LED, test points TP1 to TP5 | done |
| 3 | front end, photodiode to filter: bias, TIA and its reference, Sallen-Key low-pass, ADC input RC | done |
| 4 | ADC and host connector: ADS7042, SPI resistors, mounting holes | done |
| 5 | footprints, ERC, netlist check, SPICE simulation | done |
| 6 | 4-layer board setup: outline, stackup, rules | done |
| 7 | placement | done |
| 8 | routing, ground and power planes, DRC | done |
| 9 | release files: Gerbers, drill files, parts list, placement file, documents, fabrication notes | done |

## Run the calculations

From this folder:

```
python calc/design_calcs.py   # writes calc/results.txt
```

Needs Python with numpy.
