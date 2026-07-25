# AstraOS

An open-source, from-scratch guide to embedded Linux on the **Radxa ZERO 3W**
(Rockchip RK3566) — from Boot ROM to a working custom Linux distribution.

Built by one engineer learning it, written for anyone who wants to learn it too.

> **Source of truth:** [`docs/PRD.md`](docs/PRD.md)

## Current status

| Phase | Focus | Status |
|---|---|---|
| 0 | Computer Fundamentals | In progress |
| 1–14 | See [`ROADMAP.md`](ROADMAP.md) | Not started |

## Quick start (Phase 0)

Requires Python 3.9+.

```bash
# Memory simulator
make -C experiments/phase0-memory run

# Address translation (MMU) demo
make -C experiments/phase0-address-translation run

# Simple CPU simulator
make -C experiments/phase0-cpu run
```

Lesson: [`docs/lessons/00-computer-fundamentals.md`](docs/lessons/00-computer-fundamentals.md)

## Repository layout

Matches the structure in the PRD (Section 13): `docs/`, `bootloader/`, `kernel/`,
`device-tree/`, `drivers/`, `rootfs/`, `buildroot/`, `yocto/`, `experiments/`,
`scripts/`, `docker/`, `images/`.

## License

- **Code** (simulators, drivers, scripts, configs): [MIT](LICENSE)
- **Written docs** under `docs/`: [CC BY-SA 4.0](LICENSE)

## Hardware target

Radxa ZERO 3W — Rockchip RK3566, ARM Cortex-A55, 64-bit ARMv8.
Later phases require a USB-to-TTL UART adapter and a microSD card.
