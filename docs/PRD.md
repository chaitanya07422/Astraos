# AstraOS
### Product Requirements Document (PRD)

| Field | Value |
|---|---|
| **Version** | 2.0 |
| **Status** | Draft |
| **Author / Owner** | Chaitanya Kadavakollu |
| **Last Updated** | July 25, 2026 |
| **Target Hardware** | Radxa ZERO 3W (Rockchip RK3566) |
| **Project Type** | Open-source educational guide (author-built, community-facing) |

> An open-source, from-scratch guide to embedded Linux on the Radxa ZERO 3W — built by one engineer learning it, written for anyone who wants to learn it too.

---

## 1. Executive Summary

AstraOS is an open-source, freely available guide to building a custom embedded Linux system from scratch on the Radxa ZERO 3W (Rockchip RK3566) — from Boot ROM to a working custom Linux distribution. It is written so that anyone with software engineering experience but no prior embedded background can follow it end to end and reproduce every result on real hardware.

The project treats the full stack — SoC internals, bootloader, kernel, device tree, drivers, root filesystem, and distribution build systems (Buildroot and Yocto) — as a single connected system to be explained, not just configured. Every lesson is written to cover not only the "happy path" but the common failure modes, mistakes, and edge cases a learner is likely to hit, so the guide holds up as a real reference rather than a personal notebook.

AstraOS is scoped and tracked like a real engineering deliverable: it has explicit success criteria, acceptance criteria per component, a risk register, and a phased plan with effort estimates. The end state is a public, open-source GitHub repository — built by the author while learning, but written for anyone who wants to learn the same thing.

---

## 2. Problem Statement

Most embedded Linux learning resources fall into one of three failure modes:

1. **Tutorial-following without understanding** — copy a Buildroot config, flash it, it boots, but the "why" at each layer (Boot ROM → SPL → U-Boot → kernel → init) is never internalized.
2. **Theory without hardware** — courses and books that explain kernel internals or ARM architecture in the abstract, with no real board, no real UART log, no real panic to debug.
3. **Fragmented, board-specific knowledge** — for a board like the Radxa ZERO 3W specifically, what documentation exists is scattered across vendor wikis, forum threads, GitHub issues, and half-finished community write-ups, each covering a narrow slice and assuming context the reader may not have.

There is no single, self-contained, freely available guide that takes a software engineer with no embedded background from "what is a Boot ROM" to "I compiled and booted a custom Linux distribution on the Radxa ZERO 3W" — covering every stage, explaining the common failure cases along the way, and letting the reader reproduce every step themselves.

AstraOS exists to be that guide: built by the author while learning, but written and structured for anyone who wants to walk the same path on the same board.

---

## 3. Goals & Objectives

**Primary goal:** produce a complete, open-source, freely available guide that takes any software engineer — with no prior embedded Linux background — from first principles to a working custom Linux distribution on the Radxa ZERO 3W, explaining every stage and the common failure cases along the way.

Supporting objectives — by project completion, the guide (and the author, in the process of writing it) should:

- Explain the full boot chain on RK3566 (Boot ROM → SPL/TPL → U-Boot → kernel → init) stage by stage, with evidence (UART logs) to back up every claim.
- Walk through cross-compiling and booting a custom Linux kernel and U-Boot build for a specific ARM64 SoC, not just `make defconfig` — including what typically goes wrong and how to recognize it.
- Cover at least five real kernel drivers (GPIO, LED, button, character device, platform device) written, loaded, and tested against physical hardware, with common loading/permission/dependency errors documented.
- Show Device Tree changes and their observable effect on the running system, including how to debug a DT change that doesn't take effect.
- Build a complete, reproducible embedded Linux image using both Buildroot and Yocto, explaining the tradeoffs between them so a reader can choose for their own project.
- Include a documented process for debugging a real kernel panic/oops using ftrace/KGDB, not just a clean "it worked" narrative.
- Be structured and written so a reader can follow it independently — without needing to ask the author directly — and reproduce the results on their own board.
- Produce a repository that also stands as credible evidence of the author's systems engineering depth — a byproduct of writing a genuinely useful guide, not the primary goal.

---

## 4. Non-Goals (Out of Scope)

To keep this project finishable, the following are explicitly **out of scope for v1.0**:

- Supporting any board other than the Radxa ZERO 3W.
- Production-grade security hardening (secure boot, verified boot chain, LUKS, SELinux) — listed only as a stretch goal.
- A GUI/desktop environment (Wayland is a stretch goal, not core scope).
- Upstreaming any driver or patch to mainline Linux or U-Boot (may be considered post-v1.0, not a v1.0 requirement).
- Supporting multiple simultaneous rootfs strategies in production — Buildroot and Yocto are both explored for learning purposes, but AstraOS does not need to maintain both as parallel "products."
- Real-time (PREEMPT_RT / RTOS) guarantees.
- Supporting boards other than the Radxa ZERO 3W. The guide is written and validated specifically against this board; porting to other RK3566 boards is a possible future project, not v1.0 scope.
- "Explaining every case" means every case within the documented scope (Phases 0–14) and the board's actual peripheral set — not an exhaustive catalog of every conceivable embedded Linux scenario.

---

## 5. Target Users / Personas

| Persona | Who | What they need from AstraOS |
|---|---|---|
| **The Learner (primary)** | Any software engineer, student, or hobbyist with no embedded background who wants to learn by building on real hardware | A free, self-contained, well-documented path that explains every stage and the common failure cases — no paid bootcamp, no assumed prior context |
| **The Author** | Backend/AI engineer with ~1.5 years experience, building AstraOS while learning it themselves | A structured way to force rigor on their own learning — writing the guide well enough for a stranger to follow is the forcing function for actually understanding each layer |
| **The Contributor (secondary)** | An engineer who has worked through part of the guide and wants to fix an error, add a case, or extend it | Clear contribution guidelines, an open license, and a repo structure that makes it obvious where a fix or addition belongs |
| **The Technical Reviewer (secondary)** | Interviewer, hiring manager, or senior engineer evaluating the author's GitHub | Fast signal on depth: real boot logs, real driver code, real debugging, and a project other people actually use — not boilerplate |

---

## 6. Success Metrics

A qualitative "it boots" is not sufficient. AstraOS is considered successful against these measurable criteria:

| Metric | Target |
|---|---|
| Board boots via self-built U-Boot + custom kernel | 100% reliable across ≥10 consecutive power cycles |
| Custom kernel drivers written, loaded, and tested on hardware | ≥ 5 |
| Device Tree modifications validated on hardware | ≥ 3, each with before/after behavior documented |
| Lessons meeting the full documentation standard (Section 12) | 15 (Phase 0–14), one per phase |
| Buildroot image builds cleanly from a fresh clone | Yes, no manual post-clone patching |
| Yocto custom layer builds a bootable image | Yes, via a single `bitbake` target |
| At least one real kernel panic reproduced and root-caused | 1, with ftrace/KGDB evidence in docs |
| Boot time optimization | Measured before/after, with a quantified improvement (target: reduce baseline boot time by ≥ 20%) |
| CI passing on `main` at v1.0 tag | Markdown lint, spell check, and build verification all green |
| Public GitHub repo with tagged v1.0 release | Yes, with release notes, checksums, and flashing instructions |
| At least one external reader (not the author) completes Phases 0–4 using only the published docs | 1, with feedback captured as a GitHub issue or discussion |
| Every lesson includes a troubleshooting / common-pitfalls section | 15/15 |
| Repository has an open-source license, CONTRIBUTING guide, and issue templates | Yes, present before the v1.0 tag |
| Flashable, hardware-verified SD card image published for every versioned milestone (v0.1, v0.5, v1.0, v2.0) | 4/4, each via GitHub Releases with checksum and flashing instructions |

---

## 7. Assumptions & Constraints

**Assumptions**
- The author has a working development machine (macOS or Linux) capable of running Docker for reproducible cross-compilation.
- The Radxa ZERO 3W has adequate public documentation (Rockchip open-source BSP, Radxa wiki, Armbian/mainline community resources) to substitute for an NDA'd full TRM.
- This is a part-time project alongside full-time work — effort estimates assume roughly 8–10 hours/week.

**Constraints**
- No JTAG/SWD debugger is assumed available by default (see Risk R5); UART is the primary debug interface.
- Yocto builds require significant local disk space (100 GB+) and a multi-hour first build — this is a known constraint on iteration speed, not a defect.
- Single-board project: no access to a device farm or multiple boards for parallel testing, so hardware availability is a single point of failure (see Risk R1).

---

## 8. Hardware & Development Environment

| Component | Spec |
|---|---|
| Board | Radxa ZERO 3W |
| SoC | Rockchip RK3566, ARM Cortex-A55, 64-bit ARMv8 |
| Storage | MicroSD (primary), eMMC (optional) |
| Debug interface | USB-to-TTL UART adapter (required, low cost) |
| Optional debug interface | JTAG/SWD debugger (stretch — improves Phase 11 debugging quality) |
| Host development machine | macOS or Linux, Docker-based build environment for reproducibility |
| Minimum host disk space | ~150 GB free (Yocto is the main driver of this requirement) |

---

## 9. System Overview

AstraOS follows the standard embedded Linux boot chain, and the project is structured around understanding and customizing every stage of it:

```
Power On → Boot ROM → SPL/TPL → U-Boot → Linux Kernel → Device Tree merge → init → Root Filesystem → Userspace
```

Each stage in this chain maps directly to a project phase (Section 14): Boot ROM/SPL/TPL/U-Boot map to Phases 3–4, kernel to Phase 5, device tree to Phase 6, drivers operate within the booted kernel in Phase 7, and root filesystem/init map to Phase 8, with Phases 9–10 replacing the hand-built rootfs with a build-system-generated one (Buildroot, then Yocto).

---

## 10. Functional Requirements

Functional requirements are grouped by the core deliverables named in the original success criteria. Each has explicit acceptance criteria.

### FR-1: Custom Bootloader
- **FR-1.1** Build U-Boot from source, cross-compiled for RK3566.
- **FR-1.2** Board boots from SD card using the self-built `idbloader.img` / `u-boot.itb`.
- **FR-1.3** Boot delay and default boot command are modified and the change is documented.
- **FR-1.4** A custom boot logo is integrated and verified on-screen or via log (if headless, verified via boot log marker).
- **Acceptance:** Board completes cold boot to U-Boot prompt using only self-built binaries, reproducibly.

### FR-2: Custom Linux Kernel
- **FR-2.1** Cross-compile a kernel (mainline or Rockchip BSP) for aarch64 targeting RK3566.
- **FR-2.2** Board boots to userspace using the custom kernel and a custom `.config`.
- **FR-2.3** At least 10 kernel config changes from the baseline defconfig are documented with rationale.
- **FR-2.4** Full `dmesg` boot log is captured and annotated stage-by-stage.
- **Acceptance:** Board boots to a working shell on the custom kernel across ≥10 consecutive reboots.

### FR-3: Custom Device Tree
- **FR-3.1** Modify and recompile the board's DTS/DTB.
- **FR-3.2** At least 3 node-level changes (e.g., peripheral enable/disable, pinmux remap, GPIO reassignment) are made and validated against real hardware behavior.
- **Acceptance:** Each DT change has a documented before/after observation (e.g., UART disabled → console silent; GPIO remapped → LED moves).

### FR-4: Device Drivers
- **FR-4.1** Implement at least 5 kernel modules: GPIO driver, LED driver, button driver, character device driver, platform driver (I2C/SPI/UART/DMA/interrupt drivers as stretch additions).
- **FR-4.2** Each driver has source code, a Makefile, a README, and a documented test procedure with observed output (`dmesg`, `/dev` or `/sys` interaction).
- **Acceptance:** Each driver loads via `insmod`/`modprobe` without kernel errors and behaves per its documented test procedure.

### FR-5: Root Filesystem
- **FR-5.1** Build a minimal BusyBox-based root filesystem by hand.
- **FR-5.2** Write a custom init script that mounts `/proc`, `/sys`, `/dev` and drops to a working shell.
- **FR-5.3** Package the rootfs so it can be flashed and tested independently of the Buildroot/Yocto pipelines.
- **Acceptance:** Board boots to an interactive shell using only the hand-built rootfs, with core filesystems mounted correctly.

### FR-6: Buildroot Image
- **FR-6.1** A Buildroot configuration produces a complete, bootable SD card image.
- **FR-6.2** The build is reproducible from a clean clone via documented `make` targets, with no manual post-clone patching.
- **Acceptance:** A fresh clone + documented build command produces a flashable, bootable image.

### FR-7: Yocto Image
- **FR-7.1** A custom Yocto meta-layer exists with at least one custom recipe.
- **FR-7.2** `bitbake <image-name>` produces a bootable image from the custom layer.
- **Acceptance:** Image boots on hardware; layer and recipe are documented well enough for someone else to reproduce the build.

---

## 11. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Reproducibility** | Any contributor can clone the repo and reproduce the documented build steps within ~1 hour of setup time (excluding compile time), using the provided Docker-based build environment |
| **Documentation quality** | Every lesson follows the 13-part documentation standard (Section 12), minimum ~800 words, with at least one diagram |
| **Recoverability** | A documented recovery procedure exists for a bricked boot (e.g., re-flash via SD, UART recovery mode) before any risky bootloader/kernel experimentation begins |
| **Maintainability** | Build scripts and Makefiles are idempotent; CI validates docs and build steps on every push to `main` |
| **Portfolio presentation** | README includes an architecture diagram, boot chain visual, and photo/log evidence of the board running |
| **Release integrity** | Every published image is flashed to a physical SD card and boot-verified on an actual Radxa ZERO 3W before the release is published — no untested images are ever released |

---

## 12. Documentation Standard

Every lesson (one per phase, 15 total) must contain, in order:

1. Introduction
2. Definitions
3. Architecture
4. Internal Workflow
5. Diagrams
6. Source Code
7. Implementation
8. Experiment
9. Result
10. Troubleshooting & Common Pitfalls
11. Summary
12. Exercises
13. References
14. Limitations / Future Improvements

Every implementation artifact (driver, build script, kernel patch, etc.) additionally includes: README, Build Script/Makefile, Configuration, Logs, Output/Screenshots, Explanation, Limitations, Future Improvements.

### Guide Writing Standards

Because AstraOS is written for readers with no embedded background, every lesson also follows these rules:

- Every acronym or term is defined the first time it appears in that lesson — a reader should never need to leave the page to look something up.
- Every command is copy-paste runnable, with the expected output shown alongside it.
- Every Troubleshooting section documents the actual error messages a learner is likely to see, not just the failure mode in the abstract.
- Where a step depends on host OS (macOS vs. Linux) or hardware revision, both paths are documented explicitly rather than assumed.

---

## 13. Repository Structure

```
astra-os/
  README.md
  LICENSE
  CONTRIBUTING.md
  CODE_OF_CONDUCT.md
  ROADMAP.md
  CHANGELOG.md
  docs/
    lessons/
    hardware/
  bootloader/
  kernel/
  device-tree/
  drivers/
  rootfs/
  buildroot/
  yocto/
  experiments/
  scripts/
  docker/
  images/
  .github/
    ISSUE_TEMPLATE/
```

**License:** since AstraOS is meant to be freely usable and buildable-upon, code (bootloader configs, drivers, scripts) should use a permissive license such as MIT, and written content (lessons, docs) a content license such as CC BY-SA 4.0 — a common pairing for open educational technical projects. The final choice is tracked as an open question (Section 18) but should be settled before the first lesson is published publicly.

---

## 14. Development Workflow

**Branching:** `main`, `develop`, `feature/kernel`, `feature/rootfs`, `feature/drivers`, `feature/device-tree`, `feature/buildroot`, `feature/docs`

**Commit convention:**
```
docs: complete lesson 01 computer architecture
kernel: compile custom Linux kernel
driver: add GPIO LED driver
rootfs: create BusyBox root filesystem
```
Prefixes: `docs:`, `lesson:`, `driver:`, `kernel:`, `boot:`, `rootfs:`, `experiment:`, `refactor:`, `fix:`

**CI/CD (GitHub Actions):** Markdown lint, spell check, build verification, kernel compilation check, Buildroot validation, documentation validation.

---

## 15. Roadmap & Phased Plan

Effort estimates assume ~8–10 hrs/week part-time. Total estimated duration: **~20–24 weeks (~5–6 months)**.

| Phase | Focus | Est. Effort | Key Deliverables | Exit / Acceptance Criteria |
|---|---|---|---|---|
| 0 | Computer Fundamentals | 1 wk | Memory simulator, address translation demo, simple CPU simulator | Can explain binary/hex, registers, cache, MMU in own words; simulators run and are documented |
| 1 | ARM64 Architecture | 1 wk | Assembly programs, register inspection, context-switch demo | Can trace ≥5 AArch64 instructions by hand; context-switch demo runs (QEMU or target) |
| 2 | RK3566 SoC | 1–2 wks | Datasheet notes, register map, hardware block diagram | Block diagram covers PMIC, clock tree, UART/GPIO/USB/DDR/eMMC; notes cite source sections |
| 3 | Boot Process | 1 wk | Annotated UART boot log, modified boot commands | Full power-on-to-shell log captured; every stage annotated |
| 4 | U-Boot | 2 wks | Custom-built U-Boot, modified env/boot script, boot logo | Boots from SD using self-built U-Boot; changes verified and documented |
| 5 | Linux Kernel | 3 wks | Custom kernel config, compiled + booted kernel | Boots to shell on custom kernel; ≥10 config changes documented |
| 6 | Device Tree | 1 wk | Modified DTS/DTB | ≥3 node changes validated on hardware with before/after notes |
| 7 | Device Drivers | 3–4 wks | ≥5 kernel modules | Each driver loads cleanly and passes its documented test |
| 8 | Root Filesystem | 1 wk | Minimal BusyBox rootfs, custom init | Boots to shell with working /proc, /sys, /dev |
| 9 | Buildroot | 2 wks | Full bootable Buildroot image | Clean-clone build produces flashable image, no manual patching |
| 10 | Yocto | 2–3 wks | Custom Yocto layer + image | `bitbake` produces bootable image from custom layer |
| 11 | Kernel Debugging | 1 wk | Reproduced + resolved kernel panic | Panic triggered, diagnosed via ftrace/KGDB, root-caused in writeup |
| 12 | Networking | 1 wk | Working network path, TCP server on-target | Board reachable over network; custom TCP server responds from host |
| 13 | Performance | 1 wk | Boot-time & memory profiling report | Before/after boot time measured; ≥20% improvement applied and quantified |
| 14 | Final Distribution | 1 wk | Tagged v1.0 release | GitHub Release with image, checksums, flashing instructions, changelog |

**Suggested versioning checkpoints:** `v0.1` after Phase 4 (custom bootloader boots), `v0.5` after Phase 8 (hand-built rootfs boots), `v1.0` after Phase 14 (full distribution), `v2.0` after stretch goals.

**Release artifacts:** every versioned checkpoint above is published as a GitHub Release, not just a git tag. Each release includes:

- A ready-to-flash SD card image (`.img`, compressed) — not just source and build instructions
- SHA256 checksum for the image
- Step-by-step flashing instructions (e.g., via `dd`, balenaEtcher, or `rkdeveloptool` as applicable) written for someone who has never flashed a board before
- A short "what you'll see" description (expected boot log / UART output) so a tester can confirm success without needing to interpret it themselves

This means a learner with their own Radxa ZERO 3W can download a release, flash it, and see AstraOS boot on real hardware without building anything — the build-it-yourself path is for people who want to go deeper, not a requirement just to try it.

---

## 16. Risks & Mitigations

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | Single board — hardware bricking or failure halts the entire project | High | Maintain a known-good recovery SD image at all times; document UART/recovery-mode procedure before any risky bootloader/kernel work; consider a second board as backup once budget allows |
| R2 | RK3566 documentation is partially closed/NDA'd | Medium | Rely on Rockchip's open-source BSP release, Radxa wiki, and Armbian/mainline community sources in place of the full TRM |
| R3 | Scope creep given full-time job constraints | High | Strict time-boxing per phase (Section 15); stretch goals explicitly parked until v1.0 is tagged |
| R4 | macOS host + cross-compilation toolchain drift | Medium | Use a Docker-based reproducible build environment for all cross-compilation, checked into `docker/` |
| R5 | Debugging kernel panics without JTAG is slow | Medium | Get a USB-UART adapter early (low cost, high value); treat JTAG/SWD as a stretch acquisition if Phase 11 debugging stalls |
| R6 | Yocto build times and disk footprint slow iteration | Medium | Use `sstate-cache` and a shared downloads mirror; keep the custom layer minimal in v1.0 scope |
| R7 | Solo long-form project — motivation/burnout risk | Medium | Publish incremental progress (e.g., short write-ups per completed phase) for external accountability |

---

## 17. Dependencies

- `aarch64-linux-gnu` cross-compilation toolchain
- Rockchip RK3566 open-source BSP / public datasheet sections
- Radxa ZERO 3W wiki and schematics
- U-Boot (mainline + Rockchip vendor tree)
- Linux kernel (mainline or Rockchip BSP)
- Buildroot
- Yocto / Poky
- USB-to-TTL UART adapter (required); JTAG/SWD debugger (optional, stretch)
- Docker (for reproducible host build environment)

---

## 18. Open Questions

- Mainline kernel vs. Rockchip BSP kernel as the primary base for Phase 5 — mainline gives cleaner learning value, BSP may have better out-of-box peripheral support. **Decision needed before Phase 5 starts.**
- Should Buildroot and Yocto both be carried to full v1.0 parity, or should Yocto be treated as a "second pass" once Buildroot's image is stable? Current plan (Section 15) treats both as core, but this should be revisited after Phase 9 based on actual time spent.
- Native Linux VM vs. Docker-on-macOS for the host build environment — affects Yocto build times materially; needs a quick benchmark before Phase 9.
- Final license choice for code vs. written content (see Section 13) — needs to be settled before Phase 0 documentation is published publicly, not deferred to v1.0.

---

## 19. Stretch Goals (Post-v1.0, Prioritized)

1. Custom shell
2. Package manager
3. Rust driver examples
4. Docker support on-target
5. Read-only root filesystem
6. Secure boot
7. OTA updates
8. Node.js hardware APIs
9. Wayland GUI

---

## 20. Definition of Done (Final Deliverables)

AstraOS v1.0 is complete when the GitHub repository contains, and CI is green on:

- Complete documentation (15 lessons meeting the Section 12 standard)
- Custom-built bootloader (U-Boot)
- Custom-compiled Linux kernel
- Custom Device Tree with validated modifications
- ≥5 working, tested device drivers
- Hand-built BusyBox root filesystem
- Reproducible Buildroot image
- Reproducible Yocto custom-layer image
- Build scripts and CI automation
- Documented experiments and debugging writeups
- Tagged `v1.0` GitHub Release with images, checksums, and flashing instructions
- Flashable, hardware-verified image published as a GitHub Release at every milestone (v0.1, v0.5, v1.0, v2.0), so a learner can test on their own board without building from source
- Guide published in a form accessible to outside readers (e.g., rendered via GitHub Pages or a docs site), not just raw markdown
- LICENSE, CONTRIBUTING.md, and issue templates in place, with issues/discussions enabled for learner questions
- Engineering notes suitable for both a professional portfolio and reuse by other learners

---

## 21. Glossary

| Term | Meaning |
|---|---|
| SPL / TPL | Secondary / Tertiary Program Loader — early boot stages before full U-Boot |
| U-Boot | Common open-source bootloader used in embedded Linux systems |
| DTS / DTB | Device Tree Source / Device Tree Blob — describes hardware to the kernel |
| PMIC | Power Management IC |
| MMU | Memory Management Unit |
| BSP | Board Support Package |
| KGDB | Kernel-mode GDB, for live kernel debugging |
| ftrace | Linux kernel function tracer |
| BitBake | Build engine used by Yocto to execute recipes |
| TRM | Technical Reference Manual (SoC-level hardware documentation) |