# AstraOS Phase 1 — Cooperative context-switch demo

Two user-space "tasks" alternate on the CPU by saving/restoring callee-saved
registers and the stack pointer — the same idea an OS uses for threads, shrunk
to something you can read in one sitting.

## Build / run

```bash
./docker/phase1/run.sh make -C experiments/phase1-context-switch run
```

## Expected output

```
=== AstraOS cooperative context-switch demo ===
main: switching into task A
  [task A] slice 1
  [task B] slice 1
  [task A] slice 2
  [task B] slice 2
  [task A] slice 3
  [task B] slice 3
  [task A] done — return to main
main: both tasks finished
```

(Task B's final "done" line may or may not print depending on which task
returns to main first; the important part is A/B slices interleaving.)

## How it works

1. `bootstrap_task` fabricates a `struct context` with `x30 = entry` and a
   private stack.
2. `switch_to(prev, next)` stores x19–x30 and SP into `*prev`, loads them from
   `*next`, then `ret` — which resumes at the saved link register.
3. Each task prints, then switches to the other.

## Limitations

- Cooperative only (no preemption / timer IRQ)
- Does not save caller-saved regs or FP/SIMD — tasks must obey AAPCS64
- Not the Linux kernel scheduler; just the register-save idea behind it
