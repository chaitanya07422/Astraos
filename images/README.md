# Baseline flashable image (Phase 3)

> **This is not a custom AstraOS build.**  
> AstraOS does not yet have a self-built bootloader/kernel image. The first
> versioned AstraOS flashable release is **v0.1 after Phase 4** (PRD).  
> Publishing an untested “AstraOS” `.img` now would violate the PRD release
> rule: never release an image that has not been boot-tested on a real board.

For **Phase 3** (capture a real UART boot log), flash a **vendor / Radxa**
image to microSD, boot the ZERO 3W, and save the serial log.

---

## Recommended image (official Radxa download)

| Field | Value |
|---|---|
| Board | Radxa ZERO 3W only (not 3E) |
| File | `radxa-zero-3w-aic8800-wifi-bt-fixed-frequency.img.xz` |
| Hosted by | Radxa |
| URL | https://dl.radxa.com/zero3/images/3w/radxa-zero-3w-aic8800-wifi-bt-fixed-frequency.img.xz |
| Size | ~910 MiB compressed (Nov 2024 listing on dl.radxa.com) |
| Docs | https://docs.radxa.com/en/zero/zero3/download |
| Install guide | https://docs.radxa.com/en/zero/zero3/getting-started/install-os |

Always re-check the [download page](https://docs.radxa.com/en/zero/zero3/download) in case Radxa publishes a newer official image.

We **do not** re-host this binary in the AstraOS git repo (too large; Radxa owns
distribution). You download it from Radxa, flash it, then paste the UART log
back into this repo.

---

## What you need

- Radxa ZERO 3W  
- microSD card (≥8 GB recommended)  
- SD card reader  
- 5 V power on the **USB 2.0 OTG Type-C** port (board is 5 V only)  
- USB-to-TTL UART adapter (**3.3 V** logic — not 5 V)  

---

## Flash steps (macOS or Linux)

### 1. Download

```bash
mkdir -p ~/Downloads/radxa-zero3w && cd ~/Downloads/radxa-zero3w
curl -L -O https://dl.radxa.com/zero3/images/3w/radxa-zero-3w-aic8800-wifi-bt-fixed-frequency.img.xz
ls -lh radxa-zero-3w-aic8800-wifi-bt-fixed-frequency.img.xz
```

### 2. Decompress

```bash
# macOS (xz usually available) or: brew install xz
xz -dk radxa-zero-3w-aic8800-wifi-bt-fixed-frequency.img.xz
# produces: radxa-zero-3w-aic8800-wifi-bt-fixed-frequency.img
```

### 3. Flash with balenaEtcher (easiest)

1. Install [balenaEtcher](https://etcher.balena.io/)  
2. **Flash from file** → select the `.img` (not the `.xz`)  
3. Select the microSD target carefully  
4. Flash and wait for **Flash Complete!**  

Radxa’s own steps: https://docs.radxa.com/en/zero/zero3/getting-started/install-os  

### 3b. Flash with `dd` (Linux/macOS advanced)

```bash
# Find the SD device FIRST — wrong disk destroys data
diskutil list          # macOS
# lsblk                # Linux

# macOS example — REPLACE diskN with your SD (not disk0!)
diskutil unmountDisk /dev/diskN
sudo dd if=radxa-zero-3w-aic8800-wifi-bt-fixed-frequency.img of=/dev/rdiskN bs=4m status=progress
diskutil eject /dev/diskN
```

---

## Wire UART (before power-on)

| ZERO 3W header | USB-TTL adapter |
|---|---|
| Pin 6 GND | GND |
| Pin 8 TX (UART2_TX_M0) | RX |
| Pin 10 RX (UART2_RX_M0) | TX |

**Serial settings:** `1500000` baud, 8N1, no flow control  
(see Phase 2 notes / Radxa serial debug docs)

### macOS capture example

```bash
# find device, often /dev/cu.usbserial-* or /dev/cu.usbmodem*
ls /dev/cu.*

# record full boot to a file (Ctrl-C when you reach a shell/login)
screen -L -Logfile ~/zero3w-boot.log /dev/cu.usbserial-XXXX 1500000
# or:
# picocom -b 1500000 /dev/cu.usbserial-XXXX | tee ~/zero3w-boot.log
```

Then power the board (insert flashed SD first).

---

## What “success” looks like for Phase 3

You should see a long UART stream covering roughly:

1. Early loader / U-Boot banners  
2. Kernel decompress / Linux boot  
3. Userspace / login or shell  

Save the full log and put it in the repo as:

```text
experiments/phase3-boot/logs/power-on-to-shell.raw.txt
```

(We will annotate every stage together after you paste or commit that file.)

---

## Recovery (keep a known-good SD)

- Keep this vendor SD as your **known-good recovery image** (PRD risk R1).  
- If a later experiment bricks boot, re-flash this same vendor image and verify
  UART output returns.  
- Maskrom / USB download recovery is documented by Radxa for deeper failures;
  we will expand that before Phase 4 custom U-Boot work.

---

## What we will *not* do

| Action | Why |
|---|---|
| Tag this as AstraOS `v0.1` | v0.1 requires self-built U-Boot that boots (Phase 4) |
| Upload a random `.img` and call it AstraOS | Untested / not ours / PRD forbids |
| Commit a 1 GB binary into git | Wrong place; use Radxa’s CDN |

When Phase 4 produces a real self-built bootloader image and **you** boot-test
it on hardware, *then* we prepare a proper GitHub Release (image + SHA256 +
flash instructions) — and only push/publish when you say so.
