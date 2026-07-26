# RK3566 / Radxa ZERO 3W — datasheet & board notes

**Phase:** 2  
**Board:** Radxa ZERO 3W  
**SoC:** Rockchip RK3566  

Citations use IDs from [`SOURCES.md`](SOURCES.md).

---

## 1. What the SoC is

RK3566 is a Rockchip application processor with:

- Quad-core Arm Cortex-A55, up to ~1.6 GHz on ZERO 3W [S2][S5]
- Arm Mali-G52-2EE GPU [S2][S5]
- 32-bit DDR controller supporting LPDDR4/LPDDR4X (among others) [S6]
- eMMC 5.1, SD/MMC, USB 2.0 OTG + hosts, optional USB 3.0 via multi-PHY [S6][S7]
- Ten UART controllers, large GPIO mux fabric [S6]
- On-chip CRU (Clock & Reset Unit) and PMU (Power Management Unit) [S6]

AstraOS cares about the **CPU + memory + boot storage + UART + GPIO + USB**
path first; display/NPU are out of Phase 2 depth.

---

## 2. Board-level block picture (ZERO 3W)

From the Radxa schematic index and ref block diagram [S1 sheets 01–03, 21]:

| Block | On ZERO 3W | Schematic sheet(s) [S1] |
|---|---|---|
| SoC | RK3566 | throughout |
| PMIC | **RK817-5** (PMIC + codec) | `21.Power_PMIC` |
| DRAM | LPDDR4 ×32-bit | `14.LPDDR4_1X32bit`, `08.RK3566_DDR PHY` |
| eMMC | Optional onboard eMMC | `15.SPI Flash/eMMC` |
| microSD | TF slot via SDMMC | `16.MicroSD Card`, `13.RK3566_Flash/SD` |
| USB | USB2 Type-C OTG + USB3 Type-C HOST | `17.TYPEC_USB3.0`, `05.RK3566_USB/...` |
| Debug UART | UART2 on 40-pin header | GPIO mux; see §5 |
| Oscillator | External **24 MHz** crystal into SoC | `06.RK3566_OSC/PLL/PMUIO` |
| Wireless | Wi-Fi 6 / BT (SDIO) — 3W only | `19.WIFI/BT-SDIO` |

Product-level summary (RAM sizes, eMMC options, ports): [S2][S5].

---

## 3. PMIC (Power Management IC)

**PMIC** = chip that turns the 5 V board input into the many rails the SoC and
DRAM need.

- ZERO 3W uses **RK817-5** labeled `PMIC+Codec` on the ref block diagram and
  `Power_PMIC` sheet [S1 sheets 03, 21].
- Connected to the SoC over **I2C0** (`I2C0_SCL_PMIC` / `I2C0_SDA_PMIC`) [S1
  sheet 06].
- Control / status nets include `PMIC_SLEEP`, `PMIC_INT_L`, `PMIC_32KOUT_SOC`
  [S1 sheet 06].
- Example rails called out on the PMIC sheet: `VDD_LOGIC` (BUCK1), `VCC_DDR`
  (BUCK path), `VCC3V3_SYS`, `VCCA1V8_PMU`, `VDDA_0V9` [S1 sheet 21].

RK3566 itself has an internal **PMU** with separate voltage domains
(`VD_CORE` / `VD_LOGIC` / `VD_NPU` / `VD_GPU` / `VD_PMU`) [S6] — the external
RK817 feeds those domains; the on-chip PMU sequences / monitors them.

Board input power: **5 V / 2 A** class on USB2 OTG Type-C (or 5 V on GPIO
header pins 2 & 4) [S5].

---

## 4. Clock tree (high level)

```
  24 MHz crystal ──▶ RK3566 OSC ──▶ PLLs (inside SoC)
                                      │
                                      ▼
                                   CRU / PMUCRU
                                      │
              ┌───────────┬───────────┼───────────┬──────────┐
              ▼           ▼           ▼           ▼          ▼
            CPU         UART       eMMC/SD      USB PHYs   GPIO/PCLK
           clocks       SCLKs       SCLKs
```

Facts we can cite:

- SoC CRU: “One oscillator with **24 MHz** clock input” [S6 CRU bullet].
- Hardware design guide: internal OSC + external 24 MHz crystal form the system
  clock; keep the series resistor on `XOUT24M` as specified [S8 § clock].
- Schematic shows `Y1 24MHz`, nets `XIN24M` / `XOUT24M` [S1 sheet 06].
- PMIC can provide a **32.768 kHz** style clock to the SoC (`PMIC_32KOUT_SOC`)
  for RTC / low-power timing [S1 sheet 06].
- Linux exposes two clock controllers: `pmucru@fdd00000`, `cru@fdd20000` [S9].

We do **not** invent PLL register recipes here — that needs TRM depth later
(U-Boot/kernel already program CRU).

---

## 5. UART

SoC feature: **10 UART** interfaces, up to ~4 Mbps class baud [S6].

On ZERO 3W for **debug console** (what you will use from Phase 3 onward):

| Item | Value | Source |
|---|---|---|
| Controller | UART2 (mux mode M0) | [S3] pin table: pin 8 `UART2_TX_M0`, pin 10 `UART2_RX_M0` |
| Header pins | 8 = TX, 10 = RX, 6 = GND | [S4] |
| Default baud | **1500000** 8N1, no flow control | [S4] |
| MMIO base | `0xfe660000` | [S9] `uart2: serial@fe660000` |

Schematic also labels UART2 on the SoC pin pages [S1].

**Wiring reminder:** USB-TTL adapter RX goes to board TX (pin 8), adapter TX to
board RX (pin 10), commons GND [S4].

---

## 6. GPIO

- SoC: large GPIO bank set; datasheet quotes on the order of **~142** GPIOs [S6][S7].
- ZERO 3W exposes a **40-pin** header, **3.3 V** logic [S3].
- Pins are **multiplexed** (GPIO vs UART vs I2C vs SPI vs PWM …). The function
  you get depends on pinmux (Device Tree / pinctrl) — Phase 6.
- Linux banks include `gpio0@fdd60000`, `gpio1@fe740000`, … [S9].

Debug UART pins are GPIO0_D1 / GPIO0_D0 when not muxed as UART2 [S3].

---

## 7. USB

SoC capabilities [S6][S7]:

- USB 2.0 OTG  
- USB 2.0 Host ×2  
- Up to one USB 3.0 Host via multi-PHY  

ZERO 3W board mapping [S2][S5][S1 sheets 05, 17]:

- **USB 2.0 Type-C OTG** — power + data / download  
- **USB 3.0 Type-C HOST**  

PHY / power nets (`USB_OTG0_*`, `USB3_HOST1_*`, AVDD rails) are on schematic
sheet 05 [S1].

---

## 8. DDR (LPDDR4)

- SoC: 32-bit DDR controller; LPDDR4/LPDDR4X supported up to the datasheet
  speed grades (e.g. LPDDR4-2133 class) [S6].
- ZERO 3W: **LPDDR4**, options **1 / 2 / 4 / 8 GB** [S2][S5].
- Schematic: `14.LPDDR4_1X32bit` + `08.RK3566_DDR PHY`; rail `VCC_DDR` from
  PMIC [S1].

Memory training / timing is handled by Boot ROM / DDR init blobs in early boot
(Phase 3–4) — Phase 2 only needs to know **where DRAM lives in the block
diagram**.

---

## 9. eMMC and microSD

SoC:

- eMMC 5.1 compatible interface (1/4/8-bit, HS200, CMD Queue) [S6]  
- SD/MMC controller for SD cards [S6]  
- Boot ROM can boot from eMMC or SDMMC [S6]  

ZERO 3W:

- Optional **onboard eMMC** (0 / 8 / 16 / 32 / 64 GB) [S2][S5]  
- Always: **microSD** slot [S2][S5]  
- Schematic sheets `15` (eMMC) and `16` (MicroSD) [S1]  

Linux eMMC host often appears as `sdhci@fe310000` [S9].

---

## 10. Open questions / limits (honest)

- Full register-level TRM detail remains partially closed [PRD R2]. Phase 2
  register map uses **public DT bases** [S9] plus datasheet feature lists [S6].
- Exact BUCK→rail binding on every SKU revision: always re-check sheet 21 of
  the schematic revision you own [S1].
- Wi-Fi/BT module details are out of Phase 2 acceptance criteria (not required
  on the exit diagram checklist).

---

## 11. What to remember for later phases

| Later phase | Why this note matters |
|---|---|
| 3 Boot | Boot ROM can use SD or eMMC; UART2 is your eyes |
| 4 U-Boot | Same UART; DRAM already initialized |
| 6 Device Tree | Pinmux for UART2_M0, GPIO banks, USB, MMC nodes |
| 7 Drivers | GPIO / UART bases from the register map |
