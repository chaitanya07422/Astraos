# Hardware documentation sources

Phase 2 notes cite these **public** sources. The full Rockchip TRM is partially
NDA-gated (PRD risk R2); we use Radxa schematics, Rockchip open datasheet /
design guide material, and the mainline/vendor device tree instead.

| ID | Document | URL / location |
|---|---|---|
| S1 | Radxa ZERO 3W Schematic v1.11 (2025-01-16) | https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_schematic_v1.11_20250116.pdf |
| S2 | Radxa ZERO 3 product page / features | https://docs.radxa.com/en/zero/zero3 |
| S3 | Radxa ZERO 3 hardware interface (40-pin GPIO) | https://docs.radxa.com/en/zero/zero3/hardware-design/hardware-interface |
| S4 | Radxa serial debug (UART pins + baud) | https://docs.radxa.com/en/zero/zero3/radxa-os/uart |
| S5 | Radxa ZERO 3W Product Brief | https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_product_brief.pdf |
| S6 | Rockchip RK3566 Datasheet (public brief/full excerpts, Rev 1.5-class) | Boardcon mirror of Rockchip datasheet: https://www.boardcon.com/download/Rockchip_RK3566_Datasheet_V1.5-20241211.pdf |
| S7 | Rockchip RK3566 Brief Datasheet (block diagram) | https://www.rock-chips.com/uploads/pdf/2022.8.26/192/RK3566%20Brief%20Datasheet.pdf |
| S8 | Rockchip RK3566 Hardware Design Guide V1.1 | Community mirror of Rockchip guide (clock / power / interface design) |
| S9 | Linux `rk356x.dtsi` (peripheral base addresses) | https://github.com/rockchip-linux/kernel/blob/develop-6.6/arch/arm64/boot/dts/rockchip/rk356x.dtsi |

When a claim depends on a source, notes use `[S#]` plus a section/sheet name.
