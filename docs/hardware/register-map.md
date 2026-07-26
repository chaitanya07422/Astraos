# RK3566 register map (learner subset)

Physical addresses from public Linux `rk356x.dtsi` [S9]. These are **MMIO**
(memory-mapped I/O) bases — CPU loads/stores to these addresses talk to
hardware blocks, not DRAM.

> Full bitfield definitions live in the Rockchip TRM (often NDA). For AstraOS
> Phase 2 we map **where** blocks live; Phase 6–7 use DT + drivers instead of
> hand-poking most registers.

Citations: [`SOURCES.md`](SOURCES.md).

---

## Address map (selected)

| Block | Base (phys) | Size (DT) | Notes | Cite |
|---|---|---|---|---|
| PMUCRU | `0xfdd00000` | — | Low-power / PMU clocks | [S9] `pmucru@fdd00000` |
| CRU | `0xfdd20000` | `0x1000` | Main Clock & Reset Unit | [S9] `cru@fdd20000` |
| GPIO0 | `0xfdd60000` | — | GPIO bank 0 (incl. UART2 pins as GPIO) | [S9] `gpio0@fdd60000` |
| UART0 | `0xfdd50000` | `0x100` | UART0 | [S9] |
| UART2 | `0xfe660000` | `0x100` | **Debug console on ZERO 3W** | [S9] `uart2@fe660000` |
| GPIO1 | `0xfe740000` | — | GPIO bank 1 | [S9] `gpio1@fe740000` |
| SDMMC2 | `0xfe000000` | `0x4000` | MMC/SD style host | [S9] |
| eMMC (SDHCI) | `0xfe310000` | `0x10000` | Onboard eMMC host | [S9] `sdhci@fe310000` |
| USB2 PHY0 | `0xfe8a0000` | — | USB2 PHY | [S9] `usb2phy0@fe8a0000` |
| USB2 PHY1 | `0xfe8b0000` | — | USB2 PHY | [S9] `usb2phy1@fe8b0000` |
| USB2PHY0 GRF | `0xfdca0000` | — | PHY general register file | [S9] |
| USB2PHY1 GRF | `0xfdca8000` | — | PHY GRF | [S9] |

DDR controller / DMC appears as a logical `dmc` node in DT [S9]; early boot
code (binary blobs / U-Boot) programs DRAM timings — not a simple “one UART
style” register block for learners to poke safely.

---

## ZERO 3W → SoC block cheatsheet

| Board function | SoC block | Base to remember |
|---|---|---|
| Debug serial | UART2 | `0xfe660000` |
| Pinmux / GPIO | GPIO0… | `0xfdd60000` (bank0) |
| Clocks / resets | CRU (+ PMUCRU) | `0xfdd20000` / `0xfdd00000` |
| eMMC | SDHCI | `0xfe310000` |
| USB PHYs | usb2phy0/1 | `0xfe8a0000` / `0xfe8b0000` |
| PMIC (external) | RK817 on I2C0 | Not an SoC MMIO base — I2C device |

---

## UART2 programming model (conceptual)

DesignWare APB UART compatible (`snps,dw-apb-uart` in DT) [S9]:

1. CRU enables `SCLK_UART2` + `PCLK_UART2`  
2. Pinmux selects UART2_M0 on GPIO0_D1/D0  
3. Driver programs baud divisors for **1 500 000** on ZERO 3 debug [S4]  
4. TX/RX data registers at offsets within the `0x100` window  

You will see this as `/dev/ttyS2` or similar once Linux boots — Phase 3+
captures the UART log long before that.

---

## How to extend this map

When you need another block:

1. Open [S9] `rk356x.dtsi`  
2. Find `foo@xxxxxxxx`  
3. Add a row here with the cite  

Do **not** invent addresses from memory.
