# AstraOS Phase 1 — AArch64 assembly programs

Bare-metal-style Linux userspace assembly (no libc) for learning the AArch64
instruction set. Runs inside the Phase 1 Docker image (`linux/arm64`).

## Programs

| File | What it shows |
|---|---|
| `hello.S` | `mov`, `adr`, `svc` — write(1, …) + exit |
| `arithmetic.S` | `add`, `sub`, `ldr`, `str`, `cmp`, conditional branch |

## Build / run

From repo root:

```bash
./docker/phase1/run.sh make -C experiments/phase1-asm all
./docker/phase1/run.sh make -C experiments/phase1-asm run
```

Expected `make run` output:

```
AstraOS Phase 1: hello from AArch64
arithmetic OK: x2=13 x3=7 x4=42 result=13
```

## Hand-trace (≥5 instructions)

Trace `arithmetic.S` from `_start` through the first `str`, filling in X0–X6
on paper. Compare with the lesson exercises.

## Limitations

- Linux syscall ABI (`svc #0`), not EL1 exception vectors (those come later)
- No libc — printing is raw `write`
