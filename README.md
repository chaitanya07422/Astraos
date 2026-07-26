# AstraOS

An open-source, from-scratch guide to embedded Linux on the **Radxa ZERO 3W**
(Rockchip RK3566) — from Boot ROM to a working custom Linux distribution.

Built by one engineer learning it, written for anyone who wants to learn it too.

> **Source of truth:** [`docs/PRD.md`](docs/PRD.md)

## Current status

| Phase | Focus | Status |
|---|---|---|
| 0 | Computer Fundamentals | Done |
| 1 | ARM64 Architecture | Done |
| 2 | RK3566 SoC | Done |
| 3–14 | See [`ROADMAP.md`](ROADMAP.md) | Not started |

## Quick start

### Phase 0 (Python 3.9+)

```bash
make -C experiments/phase0-memory run
make -C experiments/phase0-address-translation run
make -C experiments/phase0-cpu run
```

Lesson: [`docs/lessons/00-computer-fundamentals.md`](docs/lessons/00-computer-fundamentals.md)

### Phase 1 (Docker)

```bash
chmod +x docker/phase1/run.sh
./docker/phase1/run.sh make -C experiments/phase1-asm run
./docker/phase1/run.sh make -C experiments/phase1-registers run
./docker/phase1/run.sh make -C experiments/phase1-context-switch run
```

Lesson: [`docs/lessons/01-arm64-architecture.md`](docs/lessons/01-arm64-architecture.md)

### Phase 2 (read + cite)

```text
docs/hardware/SOURCES.md
docs/hardware/rk3566-notes.md
docs/hardware/register-map.md
docs/hardware/block-diagram.md
```

Lesson: [`docs/lessons/02-rk3566-soc.md`](docs/lessons/02-rk3566-soc.md)

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
