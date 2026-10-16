# ORX-LITE revision A: fabrication and assembly notes

One-channel optical receiver, 4-layer board, 50 × 40 mm. The files in this folder build
revision A. The KiCad 9 design files are in `hardware/`.

## Files

| File | What it is | Who uses it |
|---|---|---|
| `gerbers/*-F_Cu.gtl` | top copper | board house |
| `gerbers/*-GND.g1` | inner layer 1: solid ground | board house |
| `gerbers/*-PWR.g2` | inner layer 2: supply tracks, rest ground | board house |
| `gerbers/*-B_Cu.gbl` | bottom copper: ground | board house |
| `gerbers/*-F_Mask.gts`, `*-B_Mask.gbs` | solder mask, top and bottom | board house |
| `gerbers/*-F_Silkscreen.gto` | white labels, top only | board house |
| `gerbers/*-F_Paste.gtp` | solder paste stencil, top only | assembler |
| `gerbers/*-Edge_Cuts.gm1` | board outline | board house |
| `gerbers/*-job.gbrjob` | layer order and stackup | board house |
| `gerbers/*-PTH.drl`, `*-NPTH.drl` | plated and non-plated holes (Excellon, mm), each with a PDF map | board house |
| `assembly/ORX-LITE_BOM_revA.csv` | parts list: 40 parts on 22 lines, grouped by value and footprint | assembler |
| `assembly/*-all-pos.csv` | placement: X, Y, rotation and side of the same 40 parts | assembler |
| `docs/ORX-LITE one-channel optical receiver.pdf` | schematic | everyone |
| `docs/*-F_Fab.pdf` | assembly drawing: part outlines and names | assembler |
| `docs/ORX-LITE_3D_revA.png` | 3D view of the assembled board | everyone |

## Board

| Item | Value |
|---|---|
| Size | 50.0 × 40.0 mm rectangle |
| Copper layers | 4 |
| Thickness | 1.6 mm |
| Material | FR4 |
| Copper | 35 µm (1 oz) on all layers as designed. Inner layers at 18 µm (0.5 oz) are also fine: no track needs controlled impedance and the supply currents are small. |
| Solder mask | green, both sides |
| Silkscreen | white, top only |
| Surface finish | ENIG recommended: its flat pads suit the 0.5 mm-pitch ADC (U5). HASL also works. |
| Vias | 42, all 0.6 mm pad with 0.3 mm hole, tented (covered by mask) on both sides. No via in a pad, no filled vias. |
| Impedance control | none. The fastest signal is the SPI clock, at most 16 MHz (ADS7042 datasheet, TI SBAS608C). |

## Stackup, top to bottom

| Layer | Thickness | Job |
|---|---|---|
| top solder mask | 0.01 mm | |
| F.Cu | 0.035 mm | all parts, signal tracks, short supply links |
| prepreg (FR4) | 0.1 mm | |
| In1.Cu "GND" | 0.035 mm | one solid ground sheet |
| core (FR4) | 1.24 mm | |
| In2.Cu "PWR" | 0.035 mm | two long supply tracks, the rest ground fill |
| prepreg (FR4) | 0.1 mm | |
| B.Cu | 0.035 mm | ground fill |
| bottom solder mask | 0.01 mm | |
| **total** | **1.6 mm** | |

These are KiCad's default thicknesses for a 1.6 mm 4-layer board. A board house's own standard
1.6 mm 4-layer stackup is fine, since no track needs controlled impedance.

## Smallest features

| Feature | On this board | Rule in KiCad |
|---|---|---|
| track width | 0.2 mm (signals), 0.4 mm (supplies) | 0.15 mm minimum |
| gap between copper of different nets | | 0.15 mm minimum |
| via | 0.6 mm pad, 0.3 mm hole | 0.15 mm copper ring minimum |
| copper to board edge | | 0.3 mm minimum |
| silkscreen text | 1.0 mm high, 0.15 mm line | 1.0 mm / 0.15 mm minimum |

All of these are at or above the standard capability of JLCPCB and PCBWay (their capability
pages, read October 2026). DRC in KiCad 9.0.7 reports 0 errors, 0 warnings and 0 unconnected
items, and the board matches the schematic.

## Holes

| Hole | Plated | Count | For |
|---|---|---|---|
| 0.3 mm | yes | 42 | vias |
| 0.7 mm | yes | 3 | D2 photodiode leads (TO-18 can) |
| 1.0 mm | yes | 10 | J1 pin header |
| 3.2 mm | no | 4 | H1 to H4, M3 mounting screws |

## Assembly

- All 40 parts sit on the top side: 38 surface-mount parts and 2 through-hole parts, D2 (S5971
  photodiode, TO-18) and J1 (2 × 5 pin header, 2.54 mm pitch).
- TP1 to TP8 are bare copper test pads and H1 to H4 are plain holes. Neither gets a part, so
  neither appears in the BOM or the placement file.
- The placement file gives X and Y in mm and rotation in degrees. Its Y axis points up, so the
  Y values are negative.
- The BOM gives value and footprint, not manufacturer part numbers. Add part numbers before an
  assembly order. The ferrite beads FB1 and FB2 (220 Ω at 100 MHz, 0603) still need a confirmed
  part number.

## Connector J1 (to the host board)

2 × 5 pin header, 2.54 mm pitch. The host board supplies 5 V and 3.3 V and reads the ADC over SPI
at 3.3 V logic.

| Pin | Signal | Pin | Signal |
|---|---|---|---|
| 1 | +5V | 2 | GND |
| 3 | +3V3 | 4 | GND |
| 5 | SCLK (host → board) | 6 | GND |
| 7 | CS_N (host → board, active low) | 8 | GND |
| 9 | SDO (board → host) | 10 | GND |
