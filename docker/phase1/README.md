# AstraOS Phase 1 Docker image

Reproducible **AArch64 Linux** toolchain for Phase 1 assembly experiments.
Uses `debian:bookworm` on `linux/arm64` so the ABI matches what you will later
run on the Radxa ZERO 3W (RK3566), even when the host is macOS.

## Requirements

- Docker Desktop (or Engine) with ability to run `linux/arm64` images

## Build the image

```bash
docker build -t astraos-phase1:bookworm docker/phase1
```

## Run commands

From the repository root:

```bash
chmod +x docker/phase1/run.sh   # once
./docker/phase1/run.sh make -C experiments/phase1-asm run
./docker/phase1/run.sh make -C experiments/phase1-registers run
./docker/phase1/run.sh make -C experiments/phase1-context-switch run
```

Interactive shell:

```bash
./docker/phase1/run.sh bash
```

## Why Docker?

PRD constraint R4: macOS + toolchain drift. All Phase 1 builds go through this
image so every learner gets the same `as` / `ld` / `gcc` / `gdb`.
