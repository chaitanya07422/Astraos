# Lesson 01 — ARM64 Architecture

**Phase:** 1  
**Hardware required:** None (Docker + `linux/arm64` image)  
**Estimated time:** 6–10 hours  
**Prerequisites:** Phase 0 complete; Docker Desktop running

> **How to use this lesson:** Read sections 1–5 for concepts. Then run each
> experiment in section 8 while reading the matching walkthrough in section 6.
> Do the exercises in section 12 before you claim Phase 1 is done.

---

## 1. Introduction

Phase 0 taught computer fundamentals with a **toy** CPU. Phase 1 uses **real
AArch64** — the same 64-bit ARM architecture inside the Radxa ZERO 3W
(Rockchip RK3566, Cortex-A55 cores).

By the end of this phase you will be able to:

1. Read and hand-trace real AArch64 instructions (`mov`, `add`, `sub`, `ldr`,
   `str`, `cmp`, branches, `svc`)
2. Explain what the general-purpose registers are for (arguments, temporaries,
   callee-saved, FP, LR, SP)
3. Inspect live register values with a program dump and with GDB
4. Explain what a **context switch** is, and see two tasks share one CPU

### What we build

| Piece | Folder | Purpose |
|---|---|---|
| Docker toolchain | `docker/phase1/` | Reproducible AArch64 Linux build/run env |
| Assembly programs | `experiments/phase1-asm/` | Hello + arithmetic (no C library) |
| Register inspection | `experiments/phase1-registers/` | See every GPR; GDB checkpoint |
| Context switch | `experiments/phase1-context-switch/` | Cooperative task A ↔ task B |

### Why Docker (not the board yet)

Your Mac may be ARM64, but macOS assembly is **not** Linux AArch64. The board
runs Linux. So Phase 1 builds and runs inside a Debian `linux/arm64` container
— same ABI you will use later on the Radxa. You do **not** need the board for
Phase 1. That starts mattering in Phases 2–4.

---

## 2. Definitions

Every acronym below is defined the first time it appears in this lesson. This
table is the cheat sheet.

| Term | Plain-English meaning |
|---|---|
| **ARM64 / AArch64** | The 64-bit way an ARMv8-A CPU runs. “ARM64” is the common name; “AArch64” is the architecture name. Same idea for our purposes. |
| **GPR** | General-Purpose Register. Small, named storage slots **inside** the CPU. AArch64 has `x0`–`x30` (64-bit). |
| **`xN` vs `wN`** | `x0` is the full 64-bit register. `w0` is the **bottom 32 bits** of the same register — not a second register. |
| **PC** | Program Counter — “which instruction am I on?” Advances by 4 bytes normally (each AArch64 instruction is 32 bits wide). |
| **SP** | Stack Pointer — address of the current stack top. Must stay **16-byte aligned** when calling functions. |
| **FP / `x29`** | Frame Pointer — points into the current function’s stack frame (helps debugging / unwinding). |
| **LR / `x30`** | Link Register — where `ret` goes back to after a function call. Set by `bl` (branch-with-link). |
| **PSTATE** | Processor state — includes condition flags N, Z, C, V (Negative, Zero, Carry, oVerflow) used by `cmp` / conditional branches. |
| **EL0 / EL1** | Exception Levels. EL0 = userspace apps. EL1 = OS kernel. Apps ask the kernel for help with `svc`. |
| **SVC** | Supervisor Call. Instruction that traps from EL0 into the kernel. Linux uses `svc #0` for system calls. |
| **Syscall** | “Please, kernel, do X.” Example: write to the terminal, exit the process. Number in `x8`, arguments in `x0`–`x5`, result in `x0`. |
| **AAPCS64** | Procedure Call Standard for AArch64 — the rules for which registers hold arguments and who must save/restore what across a call. |
| **Caller-saved** | Registers a function may freely overwrite. If the **caller** still needs them after the call, the caller must save them first. Roughly `x0`–`x18`. |
| **Callee-saved** | Registers a function must put back before returning, if it changes them. `x19`–`x28` (and FP/LR if used). |
| **Context** | A saved snapshot of the registers (and stack pointer) needed to resume a task later. |
| **Context switch** | Save task A’s context, load task B’s context — so one CPU can take turns running both. |
| **Cooperative** | Tasks switch only when they call `switch_to` on purpose. No timer interrupt steals the CPU (preemption comes later in OS land). |
| **Assembler (`as`)** | Turns `.S` text into machine-code object files (`.o`). |
| **Linker (`ld`)** | Combines `.o` files into an executable. |
| **GDB** | GNU Debugger — can stop a program and print register values. |

---

## 3. Architecture

### Big picture

```
┌─────────────────────────────────────────────────────────────┐
│                     AArch64 CPU core                        │
│                                                             │
│   Registers:  x0..x30   SP   PC   PSTATE (flags)            │
│                                                             │
│   EL0 (userspace app)  ── svc #0 ──▶  EL1 (Linux kernel)    │
│         ▲                                      │            │
│         │         result back in x0            │            │
│         └──────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
              │
              │  Phase 1 programs live here
              ▼
     hello · arithmetic · register_inspect · context_switch
     (inside Docker linux/arm64 — same ABI as the board will use)
```

The RK3566 has **four** Cortex-A55 cores. Each can run AArch64. Phase 1 only
needs to understand **one** core’s registers and instructions. SoC blocks
(UART, GPIO, clocks) are Phase 2.

### How Phase 0 maps to Phase 1

| Phase 0 idea | Phase 1 reality |
|---|---|
| Toy registers R0–R7 | Real GPRs `x0`–`x30` + SP |
| Toy `LOAD` / `STORE` | `ldr` / `str` |
| Toy `ADD` / `SUB` | `add` / `sub` |
| Toy `JMP` / `BEQ` | `b` / `b.eq` / `b.ne` / … |
| Toy `HALT` | `svc` exit syscall (or return to OS) |
| Software “MMU demo” | Still not programming the real MMU — Linux already set it up for our process |

---

## 4. Internal Workflow

### 4.1 Fetch → decode → execute (same loop, real instructions)

1. **Fetch** the 32-bit instruction at PC  
2. **Decode** what it means (e.g. “add these two registers”)  
3. **Execute** it (update a register, memory, or PC)  
4. Normally PC ← PC + 4; a branch sets PC to a new address

### 4.2 The registers you will actually use

Think of the GPRs as labeled boxes:

```
x0  x1  x2  x3  x4  x5  x6  x7     ← arguments / return value
x8                              ← syscall number (Linux)
x9  x10 x11 x12 x13 x14 x15     ← temporaries
x16 x17                         ← linker/veneer scratches
x18                             ← platform (leave alone)
x19 x20 … x28                   ← callee-saved (must restore)
x29  = FP (frame pointer)
x30  = LR (return address)
sp   = stack pointer
```

**Rule of thumb for reading code:**

- Seeing `mov x0, #…` before `svc` → preparing a syscall argument  
- Seeing `mov x8, #64` → selecting which syscall (`write`)  
- Seeing `stp x29, x30, [sp, #…]!` → function prologue saving FP/LR  

### 4.3 Linux AArch64 syscall recipe

To ask the kernel to do something:

```
1. Put arguments in x0, x1, x2, … (as needed)
2. Put the syscall number in x8
3. Execute:  svc #0
4. Read the result from x0 (bytes written, error code, etc.)
```

Numbers used in this phase:

| Syscall | Number (`x8`) | Meaning |
|---|---|---|
| `write` | 64 | Write bytes to a file descriptor |
| `exit` | 93 | Terminate the process |

`write(1, buf, len)` means: file descriptor **1** = standard output (your
terminal).

### 4.4 Load and store (memory)

Registers are not enough — data also lives in RAM.

| Instruction | Meaning |
|---|---|
| `ldr x4, [x5]` | Load 8 bytes from address in `x5` into `x4` |
| `str x2, [x5]` | Store 8 bytes from `x2` into address in `x5` |
| `adr x5, label` | Put the address of `label` into `x5` (PC-relative) |

### 4.5 Compare and branch

```
cmp  x2, #13     // compute x2 - 13; set flags (especially Z if equal)
b.ne fail        // if Not Equal (Z clear), jump to fail
b    exit        // unconditional jump
```

### 4.6 Building a wide constant with `movz` / `movk`

A single `mov` cannot always load an arbitrary 64-bit pattern. So we build it
in 16-bit chunks:

```
movz x0, #0xA0A0                 // set bits 15:0, zero the rest
movk x0, #0xA0A0, lsl #16        // keep other bits; set 31:16
movk x0, #0xA0A0, lsl #32        // set 47:32
movk x0, #0xA0A0, lsl #48        // set 63:48
// x0 is now 0xA0A0A0A0A0A0A0A0
```

- **`movz`** = move and **zero** other bits  
- **`movk`** = move and **keep** other bits  

### 4.7 What a context switch does

One CPU. Two tasks. They take turns:

```
1. Save current task’s important registers into its "context" struct
2. Load the next task’s registers from its struct
3. ret  →  CPU continues in the next task as if it never left
```

We only save **callee-saved** registers + FP + LR + SP, because that is enough
for correct C code that follows AAPCS64. (A full OS also saves caller-saved
regs, FP/SIMD regs, and more — later.)

---

## 5. Diagrams

### 5.1 Hand-trace of `arithmetic.S` (the five+ instructions you must know)

Start with unknown/irrelevant registers. After each line, only changed regs matter:

```
Instruction              x0   x1   x2   x3   x4   x5   x6   memory
───────────────────────  ──   ──   ──   ──   ──   ──   ──   ──────
mov  x0, #10             10    ·    ·    ·    ·    ·    ·
mov  x1, #3              10    3    ·    ·    ·    ·    ·
add  x2, x0, x1          10    3   13    ·    ·    ·    ·
sub  x3, x0, x1          10    3   13    7    ·    ·    ·
adr  x5, value           10    3   13    7    ·   &value ·
ldr  x4, [x5]            10    3   13    7   42   &value ·   (loaded 42)
adr  x5, result          10    3   13    7   42   &result ·
str  x2, [x5]            10    3   13    7   42   &result ·   result:=13
ldr  x6, [x5]            10    3   13    7   42   &result 13
```

If you can fill that table yourself without looking, you meet the “trace ≥5
instructions by hand” exit criterion.

### 5.2 Syscall path for `hello.S`

```
_start
  x0=1 (stdout)     x1=&msg     x2=len     x8=64 (write)
       │
       ▼
    svc #0  ──────▶  Linux kernel writes bytes to your terminal
       │
       ▼
  x0=0 (exit code)  x8=93 (exit)
       │
       ▼
    svc #0  ──────▶  process ends
```

### 5.3 Context switch (cooperative)

```
                 switch_to(&main, &A)
  main ──────────────────────────────────▶  task A (slice 1)
                                              │ switch_to(&A, &B)
                                              ▼
                                            task B (slice 1)
                                              │ switch_to(&B, &A)
                                              ▼
                                            task A (slice 2)
                                              │
                                             ...
                                              ▼
                                            task A done
                                              │ switch_to(&A, &main)
                                              ▼
                                            main prints "finished"
```

Each arrow is: **save prev registers → load next registers → `ret`**.

### 5.4 `struct context` memory layout (must match `switch.S`)

```
offset  field
  0     x19
  8     x20
 16     x21
 24     x22
 32     x23
 40     x24
 48     x25
 56     x26
 64     x27
 72     x28
 80     x29 (FP)
 88     x30 (LR / resume address)
 96     sp
```

If C and assembly disagree on this layout, you get a crash. That is a common
embedded bug pattern — keep layouts in sync.

---

## 6. Source Code — full walkthrough

### 6.1 Docker environment — `docker/phase1/`

| File | Role |
|---|---|
| `Dockerfile` | Debian bookworm + `gcc`, `binutils`, `gdb`, `make` |
| `run.sh` | Builds the image once; runs any command inside it with your repo mounted at `/work` |
| `README.md` | Short usage notes |

You almost always type:

```bash
./docker/phase1/run.sh <command>
```

instead of running `<command>` on the Mac host.

### 6.2 `hello.S` — line by line

Path: `experiments/phase1-asm/hello.S`

```asm
.section .rodata          // read-only data
msg:
    .ascii "AstraOS Phase 1: hello from AArch64\n"
msg_len = . - msg         // assembler computes byte length

.section .text
.global _start            // linker entry point (no libc, so not main)
_start:
    mov  x0, #1           // arg0: fd = 1 (stdout)
    adr  x1, msg          // arg1: pointer to message
    mov  x2, #msg_len     // arg2: how many bytes
    mov  x8, #64          // syscall number: write
    svc  #0               // enter kernel

    mov  x0, #0           // exit status 0
    mov  x8, #93          // syscall number: exit
    svc  #0               // process ends (never returns)
```

**Instructions to know here:** `mov`, `adr`, `svc`.

### 6.3 `arithmetic.S` — line by line

Path: `experiments/phase1-asm/arithmetic.S`

**Data:**

```asm
value:  .quad 42     // 8-byte integer 42 in RAM
result: .quad 0      // 8-byte slot we will write
```

**Core math + memory (hand-trace these):**

```asm
mov  x0, #10
mov  x1, #3
add  x2, x0, x1      // 10+3 → 13
sub  x3, x0, x1      // 10-3 → 7
adr  x5, value
ldr  x4, [x5]        // load 42
adr  x5, result
str  x2, [x5]        // store 13
ldr  x6, [x5]        // reload to verify
```

**Checks:** `cmp` + `b.ne` jump to `fail` if any value is wrong; otherwise
`write` the OK message and `exit`.

**Instructions to know here:** `mov`, `add`, `sub`, `adr`, `ldr`, `str`,
`cmp`, `b.ne`, `b`, `svc`.

### 6.4 Register inspection — `fill_regs` + `main`

Paths:

- `experiments/phase1-registers/registers.S`
- `experiments/phase1-registers/main.c`

**Idea:** C calls `fill_regs(&snapshot)`. Assembly puts distinctive values in
many registers, copies them into the struct, then returns. C prints the struct.

Important details inside `fill_regs`:

1. **Prologue** saves FP/LR and `x19`/`x20` (callee-saved we will clobber):

   ```asm
   stp x29, x30, [sp, #-32]!
   mov x29, sp
   stp x19, x20, [sp, #16]
   ```

2. Save the incoming pointer (`x0` = `&snapshot`) into `x9`, because we are
   about to overwrite `x0` with a demo pattern.

3. Build `x0 = 0xA0A0A0A0A0A0A0A0` with `movz`/`movk`; set `x1`..`x8`,
   `x10`..`x17` to small integers; set `x19=0x13`, `x20=0x14`.

4. `str` each register into the snapshot array.

5. Label `fill_regs_ready` — **GDB breaks here** while demo values are still
   live (before we restore `x19`/`x20`).

6. **Epilogue** restores callee-saved regs and returns:

   ```asm
   ldp x19, x20, [sp, #16]
   ldp x29, x30, [sp], #32
   ret
   ```

### 6.5 Context switch — `switch_to` + two tasks

Paths:

- `experiments/phase1-context-switch/switch.S`
- `experiments/phase1-context-switch/main.c`

**`switch_to(prev, next)`** (assembly):

```text
x0 = prev context pointer
x1 = next context pointer

for each callee-saved register:
    store it into prev
for each callee-saved register:
    load it from next
sp = next->sp
ret                 // goes to next->x30
```

**Bootstrapping a new task** (C):

- Give the task its own stack array  
- Set `ctx->x30 = (uint64_t)task_entry` so the first `ret` jumps into the task  
- Set `ctx->sp` to the top of that stack (16-byte aligned)

**What you should see when it runs:**

```
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

The interleaving **is** the proof the context switch works.

---

## 7. Implementation

| Choice | Why |
|---|---|
| Docker `linux/arm64` | Same Linux AArch64 ABI as the board; avoids macOS assembler mismatch (PRD R4) |
| Pure asm for hello/arithmetic | You see `svc` clearly — no libc hiding it |
| C + asm for registers / switch | Matches how real systems mix languages |
| Save only callee-saved in `switch_to` | Enough for AAPCS64-correct C; small enough to read |
| `O0 -g` for C demos | Easier GDB; no optimizer shuffling |

Build tools inside the container: `as`, `ld`, `gcc`, `gdb`, `make`.

---

## 8. Experiment

### Prerequisites

```bash
docker version
# Expected: Client and Server version info (Engine running)
```

If Docker is not running, start Docker Desktop first.

Confirm the container is AArch64:

```bash
chmod +x docker/phase1/run.sh
./docker/phase1/run.sh uname -m
# Expected:
# aarch64
```

### Experiment A — assembly programs

```bash
./docker/phase1/run.sh make -C experiments/phase1-asm run
```

**Expected output:**

```
AstraOS Phase 1: hello from AArch64
arithmetic OK: x2=13 x3=7 x4=42 result=13
```

### Experiment B — register inspection

```bash
./docker/phase1/run.sh make -C experiments/phase1-registers run
```

**Expected highlights in the printout:**

```
x0  = 0xa0a0a0a0a0a0a0a0
x1  = 0x0000000000000001
x19 = 0x0000000000000013
```

Then inspect with GDB (non-interactive):

```bash
./docker/phase1/run.sh make -C experiments/phase1-registers gdb-demo
```

**Expected:** at breakpoint `fill_regs_ready`, GDB shows `x0` pattern, `x1=1`,
`x19=0x13`, `x20=0x14`.

### Experiment C — context switch

```bash
./docker/phase1/run.sh make -C experiments/phase1-context-switch run
```

**Expected:** A/B slices alternate 1→2→3, then main resumes (see section 6.5).

---

## 9. Result

Reference run (Docker Desktop, Debian bookworm `linux/arm64`, 2026-07-26):

| Demo | Observed result |
|---|---|
| `phase1-asm` | Hello line + `arithmetic OK: x2=13 x3=7 x4=42 result=13` |
| `phase1-registers` | Distinctive GPR dump; GDB shows demo values at `fill_regs_ready` |
| `phase1-context-switch` | Interleaved A/B slices; return to main |

### Exit / Acceptance Criteria (from PRD)

| Criterion | How this phase meets it |
|---|---|
| Can trace ≥5 AArch64 instructions by hand | Section 5.1 + Exercise 1 (`mov`/`add`/`sub`/`ldr`/`str` at minimum) |
| Context-switch demo runs (QEMU or target) | `phase1-context-switch` runs under Docker `linux/arm64` userspace |

---

## 10. Troubleshooting & Common Pitfalls

### `Cannot connect to the Docker daemon`

```
ERROR: Cannot connect to the Docker daemon at unix:///Users/.../docker.sock
Is the docker daemon running?
```

**Cause:** Docker Desktop is stopped.  
**Fix:** Open Docker Desktop → wait until Engine is running → retry.

### Wrong architecture / `exec format error`

```
exec /usr/bin/make: exec format error
```

**Cause:** Image built for amd64 (or host tools used by mistake).  
**Fix:**

```bash
docker build --platform linux/arm64 -t astraos-phase1:bookworm docker/phase1
./docker/phase1/run.sh uname -m
# must print: aarch64
```

### Running `make` on macOS instead of in Docker

```
as: unrecognized option … 
```

or a Mach-O binary that is not a Linux ELF.

**Cause:** Host assembler targets Darwin, not Linux.  
**Fix:** Prefix every build/run with `./docker/phase1/run.sh`.

### `arithmetic FAIL`

```
arithmetic FAIL
```

**Cause:** Values no longer match the compares (edited immediates, broken
`ldr`/`str`, etc.).  
**Fix:** Re-trace Section 5.1; run `make -C experiments/phase1-asm clean run`
inside Docker.

### GDB ASLR warning

```
warning: Error disabling address space randomization: Operation not permitted
```

**Cause:** Container cannot change ASLR. Harmless for this lesson.  
**Fix:** Ignore; register values at the breakpoint are still correct.

### Context switch segfault

```
Segmentation fault
```

**Cause (common):** `struct context` field order changed in C but not in
`switch.S` offsets; or stack not 16-byte aligned.  
**Fix:** Keep the layout in Section 5.4 identical on both sides; keep
`__attribute__((aligned(16)))` on stacks.

### Confusing `x0` and `w0`

**Pitfall:** Thinking they are two different registers.  
**Reality:** Same register, 64-bit vs 32-bit view. Prefer `x*` in this lesson.

### Expecting task B’s “done” line

**Pitfall:** Wondering why only task A prints “done”.  
**Reality:** After B’s third slice it switches back to A; A then returns to
main. B never runs its epilogue. The important proof is the **interleaved
slices**.

### “Docker isn’t QEMU”

**Pitfall:** Worrying the PRD required QEMU specifically.  
**Reality:** PRD says “QEMU **or** target.” Docker `linux/arm64` is a valid
runnable AArch64 Linux userspace path for Phase 1. On Apple Silicon it is
often native, not emulated.

---

## 11. Summary

Write these in your own words when you are done (Phase 1 self-check):

1. **AArch64** gives you `x0`–`x30` and `sp`. Linux syscalls use `x8` + `svc #0`.  
2. **`ldr`/`str`** move data between registers and memory; **`add`/`sub`/`mov`**
   stay in registers.  
3. **AAPCS64** decides which registers are arguments and which must be restored.  
4. A **context switch** saves one task’s registers/SP and loads another’s so
   tasks share one CPU.  
5. You can **hand-trace** a short AArch64 sequence and predict register values.

Next: **Phase 2 — RK3566 SoC** (block diagram, clocks, UART/GPIO notes).

---

## 12. Exercises

1. **Hand-trace (≥5 instructions).** Without looking at Section 5, fill X0–X4
   after each line:

   ```
   mov x0, #20
   mov x1, #5
   add x2, x0, x1
   sub x3, x2, x1
   mov x4, x3
   ```

   Expected final: `x0=20 x1=5 x2=25 x3=20 x4=20`.

2. **Second `write`.** Edit `hello.S` to print two lines (two `write` syscalls),
   then one `exit`. Show the output.

3. **Why callee-saved?** In one short paragraph: why `switch_to` saves
   `x19`–`x28` but not `x0`–`x7` for this C cooperative demo.

4. **Third task.** Add `task_c` and round-robin A→B→C→A for three slices each.

5. **GDB + LR.** At `fill_regs_ready`, what is `x30`? How does it relate to
   returning into `main`?

---

## 13. References

- AstraOS PRD — [`docs/PRD.md`](../PRD.md) (Phase 1 roadmap row)  
- Phase 0 lesson — [`00-computer-fundamentals.md`](00-computer-fundamentals.md)  
- [ARM Architecture Reference Manual (Armv8-A)](https://developer.arm.com/documentation/ddi0487/latest)  
- [AAPCS64 — Procedure Call Standard](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst)  
- [Linux syscall numbers (asm-generic unistd.h)](https://github.com/torvalds/linux/blob/master/include/uapi/asm-generic/unistd.h)  

Experiment READMEs:

- [`experiments/phase1-asm/README.md`](../../experiments/phase1-asm/README.md)  
- [`experiments/phase1-registers/README.md`](../../experiments/phase1-registers/README.md)  
- [`experiments/phase1-context-switch/README.md`](../../experiments/phase1-context-switch/README.md)  
- [`docker/phase1/README.md`](../../docker/phase1/README.md)

---

## 14. Limitations / Future Improvements

- Userspace only — no bare-metal EL1 bring-up, IRQ, or programming the real MMU  
- Context switch does not save FP/SIMD (`v0`–`v31`) or caller-saved GPRs  
- Not yet running on the physical Radxa ZERO 3W  
- Future ideas: QEMU `virt` machine, bare-metal `crt0`, on-target static
  binaries after U-Boot/kernel exist  

---

*End of Lesson 01 — ARM64 Architecture.*
