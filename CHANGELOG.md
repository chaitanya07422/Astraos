# Changelog

All notable changes to AstraOS are documented here.
Format inspired by [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added

- Repository scaffold matching PRD Section 13 layout
- Dual license: MIT (code) + CC BY-SA 4.0 (docs)
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, Cursor project rules
- Phase 0 computer-fundamentals simulators under `experiments/`
  - `phase0-memory` — byte-addressable little-endian memory + hex dump
  - `phase0-address-translation` — page table + TLB + faults
  - `phase0-cpu` — toy CPU with fetch–decode–execute and sample programs
- Lesson 00: [`docs/lessons/00-computer-fundamentals.md`](docs/lessons/00-computer-fundamentals.md)
- Phase 1 Docker image: `docker/phase1/` (`linux/arm64` Debian bookworm)
- Phase 1 experiments:
  - `phase1-asm` — hello + arithmetic (svc, add/sub/ldr/str)
  - `phase1-registers` — GPR snapshot + GDB inspection
  - `phase1-context-switch` — cooperative task switch in AArch64 asm
- Lesson 01: [`docs/lessons/01-arm64-architecture.md`](docs/lessons/01-arm64-architecture.md)
- Phase 2 hardware pack under `docs/hardware/`:
  - `SOURCES.md` — citation bibliography
  - `rk3566-notes.md` — datasheet/board notes
  - `register-map.md` — public MMIO bases
  - `block-diagram.md` — PMIC, clocks, UART, GPIO, USB, DDR, eMMC
- Lesson 02: [`docs/lessons/02-rk3566-soc.md`](docs/lessons/02-rk3566-soc.md)

### Phase status

- Phase 0 (Computer Fundamentals) — complete against PRD exit criteria
- Phase 1 (ARM64 Architecture) — complete against PRD exit criteria
- Phase 2 (RK3566 SoC) — complete against PRD exit criteria
