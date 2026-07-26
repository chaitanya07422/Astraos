# AstraOS Roadmap

Tracked against [`docs/PRD.md`](docs/PRD.md) Section 15. Phases must complete in
order; a phase is only marked done when its Exit / Acceptance Criteria are met.

| Phase | Focus | Status | Notes |
|---|---|---|---|
| 0 | Computer Fundamentals | Done | Memory sim, address translation, CPU sim + lesson 00 — exit criteria met |
| 1 | ARM64 Architecture | Done | AArch64 asm, register inspect, context-switch via Docker arm64 + lesson 01 |
| 2 | RK3566 SoC | Not started | |
| 3 | Boot Process | Not started | |
| 4 | U-Boot | Not started | → v0.1 checkpoint after this phase |
| 5 | Linux Kernel | Not started | |
| 6 | Device Tree | Not started | |
| 7 | Device Drivers | Not started | |
| 8 | Root Filesystem | Not started | → v0.5 checkpoint after this phase |
| 9 | Buildroot | Not started | |
| 10 | Yocto | Not started | |
| 11 | Kernel Debugging | Not started | |
| 12 | Networking | Not started | |
| 13 | Performance | Not started | |
| 14 | Final Distribution | Not started | → v1.0 checkpoint |

## Versioned checkpoints

| Tag | After phase | Artifacts required |
|---|---|---|
| v0.1 | 4 | Flashable image, SHA256, flashing instructions, boot-tested |
| v0.5 | 8 | Flashable image, SHA256, flashing instructions, boot-tested |
| v1.0 | 14 | Full distribution release |
| v2.0 | Stretch goals | Post-v1.0 |
