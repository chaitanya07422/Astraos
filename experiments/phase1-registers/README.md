# AstraOS Phase 1 — Register inspection

Shows AArch64 general-purpose registers (GPRs) two ways:

1. Runtime spill from assembly into a C struct, printed by `main`
2. GDB `info registers` at a breakpoint (batch script via `make gdb-demo`)

## Build / run

```bash
./docker/phase1/run.sh make -C experiments/phase1-registers run
./docker/phase1/run.sh make -C experiments/phase1-registers gdb-demo
```

## What to look for

- `x0` pattern `0xA0A0A0A0A0A0A0A0` after `movz`/`movk`
- `x1`..`x7` = 1..7
- `x19` = `0x13` (callee-saved; restored before return so C's x19 is safe)
- `x29` = frame pointer, `x30` = link register (return address)
- `sp` = stack pointer inside `fill_regs`

## AAPCS64 cheat sheet

| Registers | Role |
|---|---|
| x0–x7 | Arguments / return value |
| x8 | Indirect result location |
| x9–x15 | Temporaries |
| x16–x17 | Intra-procedure-call scratches |
| x18 | Platform register (leave alone) |
| x19–x28 | Callee-saved |
| x29 | Frame pointer (FP) |
| x30 | Link register (LR) |
| sp | Stack pointer |

## Limitations

- Does not cover NEON/FP registers (v0–v31) — stretch for later
- x18 value is whatever the platform left it; we do not force it
