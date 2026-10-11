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

## Files

```
docs/components.md       every part: what it is, why, how it is connected, where it came from
docs/design_process.md   the whole design: needs, formulas, values, reasoning
calc/design_calcs.py     every number in design_process.md (writes calc/results.txt)
tools/check_schematic.py compares the KiCad schematic with the intended design
hardware/                the KiCad project
```

## Steps

| Step | What | State |
|---|---|---|
| 1 | KiCad project, page setup | done |
| 2 | power input: J1, ferrite beads, PWR_FLAGs | done |
| 3 | regulators U1, U2 | done |
| 4 | LED and test points | done |
| 5 | photodiode bias | to do |
| 6 | TIA and its reference | to do |
| 7 | filter and ADC input network | to do |
| 8 | ADC and SPI lines | to do |
| 9 | footprints, ERC, schematic check | to do |
| 10 | SPICE simulation | to do |
| 11 | board setup: outline, 4-layer stackup, rules | to do |
| 12 | placement | to do |
| 13 | routing | to do |
| 14 | manufacturing files | to do |

## Check the schematic

From this folder:

```
python tools/check_schematic.py               # values and connections
python tools/check_schematic.py --footprints  # also footprints
```

It exports KiCad's netlist with kicad-cli and compares every pin with the design.
Needs Python with numpy only for `calc/`; the checker needs plain Python and KiCad 9.
