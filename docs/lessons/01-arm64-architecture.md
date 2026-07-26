# Lesson 01 — ARM64 Architecture

**Phase:** 1  
**Hardware required:** None (Docker + `linux/arm64` image)  
**Estimated time:** 6–10 hours  
**Prerequisites:** Phase 0 complete; Docker Desktop running

---

## 1. Introduction

Phase 0 used a toy CPU. Phase 1 switches to **real AArch64** — the 64-bit ARM
architecture used by the Radxa ZERO 3W's Rockchip RK3566 (Cortex-A55 cores).

You will:

1. Assemble and run small AArch64 programs (syscalls, arithmetic, load/store)
2. Inspect general-purpose registers (GPRs) at runtime and under GDB
3. Run a cooperative **context-switch** demo that saves/restores callee-saved
   registers and the stack pointer — the same idea behind threads/OS scheduling

Everything runs in the Phase 1 Docker image so macOS hosts get a Linux AArch64
ABI matching the eventual board target (PRD risk R4).

---

## 2. Definitions

| Term | Definition |
|---|---|
| **AArch64** | 64-bit execution state of the ARMv8-A architecture (also called ARM64). |
| **GPR** | General-Purpose Register — `x0`–`x30` are 64-bit; `w0`–`w30` are the low 32 bits of the same registers. |
| **W-register** | 32-bit view of a GPR (`w0` is the bottom half of `x0`). |
| **PC** | Program Counter — address of the current instruction (not a general `x` register you `mov` freely in userspace the same way). |
| **SP** | Stack Pointer — must stay 16-byte aligned under the Procedure Call Standard. |
| **FP / x29** | Frame Pointer — points into the current stack frame. |
| **LR / x30** | Link Register — return address for `bl` / `ret`. |
| **AAPCS64** | ARM Architecture Procedure Call Standard for AArch64 — who saves which registers across calls. |
| **Caller-saved** | Registers the caller must assume are clobbered by a call (`x0`–`x18` roughly). |
| **Callee-saved** | Registers a function must restore before returning (`x19`–`x28`, and usually FP/LR if used). |
| **SVC** | Supervisor Call — userspace trap into the kernel (`svc #0` for Linux syscalls). |
| **Syscall** | Request to the OS (e.g. `write`, `exit`). Number goes in `x8`; args in `x0`–`x5`. |
| **Context** | Saved register set (and SP) that lets you resume a task later. |
| **Context switch** | Saving one task's context and loading another's so they share one CPU. |
| **QEMU / Docker arm64** | Ways to run AArch64 Linux without the board; this phase uses Docker `linux/arm64`. |

---

## 3. Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     AArch64 CPU                          │
│  x0..x30   SP   PC   PSTATE (flags N,Z,C,V, …)           │
│                                                          │
│  Userspace (EL0)  --svc-->  Kernel (EL1)                 │
└──────────────────────────────────────────────────────────┘
         │
         │  Phase 1 runs here (Linux userspace in Docker)
         ▼
   hello / arithmetic / register_inspect / context_switch
```

RK3566 has four Cortex-A55 cores; each core is an AArch64 PE (Processing
Element). Phase 1 does not touch SoC peripherals yet — that is Phase 2.

---

## 4. Internal Workflow

### Instruction execution

Same fetch → decode → execute loop as Phase 0, but with real encodings:

1. Fetch 32-bit instruction at PC  
2. Decode opcode (e.g. `ADD Xd, Xn, Xm`)  
3. Execute; update PC (+4, or branch target)

### Linux AArch64 syscall path

```
mov x0, arg0
mov x1, arg1
...
mov x8, #syscall_number
svc #0                 // enter kernel; result returns in x0
```

Examples used here: `__NR_write` = 64, `__NR_exit` = 93.

### Calling convention (simplified AAPCS64)

| Registers | Role |
|---|---|
| x0–x7 | Arguments / return value |
| x9–x15 | Temporaries |
| x19–x28 | Callee-saved |
| x29 / x30 | FP / LR |
| sp | Stack (16-byte aligned) |

### Context switch

`switch_to(prev, next)`:

1. Store x19–x30 and SP into `*prev`  
2. Load them from `*next`  
3. `ret` — resumes at the saved LR (task entry or return site)

---

## 5. Diagrams

### Hand-trace map for `arithmetic.S` (first instructions)

```
mov x0, #10     →  x0=10
mov x1, #3      →  x1=3
add x2, x0, x1  →  x2=13
sub x3, x0, x1  →  x3=7
ldr x4, [value] →  x4=42
str x2, [result]→  mem[result]=13
```

### Context switch

```
 main ──switch_to──▶ task A ──▶ task B ──▶ task A ──▶ … ──▶ main
              save main                 save A / load B
```

---

## 6. Source Code

| Artifact | Path |
|---|---|
| Docker image | [`docker/phase1/`](../../docker/phase1/) |
| Assembly programs | [`experiments/phase1-asm/`](../../experiments/phase1-asm/) |
| Register inspection | [`experiments/phase1-registers/`](../../experiments/phase1-registers/) |
| Context switch | [`experiments/phase1-context-switch/`](../../experiments/phase1-context-switch/) |

---

## 7. Implementation

- **Assembler / linker:** GNU `as` + `ld` (hello, arithmetic) and `gcc` for C+asm
- **Environment:** `astraos-phase1:bookworm` Debian arm64 container
- **No board required** — criteria allow QEMU or target; Docker arm64 satisfies "runs"
- Pure syscall asm for hello/arithmetic (no libc) so the `svc` path is visible
- Context switch saves only callee-saved GPRs + FP/LR/SP (teaching subset)

---

## 8. Experiment

### Prerequisites

```bash
docker version
# Expected: Client/Server version lines (Docker Desktop running)
```

First-time image build (automatic via helper):

```bash
chmod +x docker/phase1/run.sh
./docker/phase1/run.sh uname -m
# Expected: aarch64
```

### Experiment A — assembly programs

```bash
./docker/phase1/run.sh make -C experiments/phase1-asm run
```

**Expected:**

```
AstraOS Phase 1: hello from AArch64
arithmetic OK: x2=13 x3=7 x4=42 result=13
```

### Experiment B — register inspection

```bash
./docker/phase1/run.sh make -C experiments/phase1-registers run
./docker/phase1/run.sh make -C experiments/phase1-registers gdb-demo
```

**Expected (runtime):** `x0 = 0xa0a0a0a0a0a0a0a0`, `x1 = 1`, `x19 = 0x13`.  
**Expected (gdb-demo):** `info registers` shows those values at `fill_regs_ready`.

### Experiment C — context switch

```bash
./docker/phase1/run.sh make -C experiments/phase1-context-switch run
```

**Expected:** interleaved `[task A]` / `[task B]` slices, then return to main.

---

## 9. Result

Reference run (Docker Desktop, `linux/arm64` Debian bookworm, 2026-07-26):

| Demo | Result |
|---|---|
| `phase1-asm` | hello + arithmetic OK line printed |
| `phase1-registers` | Distinctive GPR snapshot printed; GDB dump at checkpoint |
| `phase1-context-switch` | A/B slices 1..3 interleaved; main resumed |

**Exit criteria:**

| Criterion | Status |
|---|---|
| Trace ≥5 AArch64 instructions by hand | Covered by exercises below + `arithmetic.S` |
| Context-switch demo runs (QEMU or target) | Met via Docker `linux/arm64` (equivalent userspace AArch64) |

---

## 10. Troubleshooting & Common Pitfalls

### `Cannot connect to the Docker daemon`

```
ERROR: Cannot connect to the Docker daemon at unix:///Users/.../docker.sock
```

**Cause:** Docker Desktop is not running.  
**Fix:** Start Docker Desktop, wait until Engine is running, retry.

### `exec format error` or wrong architecture

```
exec /usr/bin/make: exec format error
```

**Cause:** Image built for the wrong CPU architecture.  
**Fix:**

```bash
docker build --platform linux/arm64 -t astraos-phase1:bookworm docker/phase1
./docker/phase1/run.sh uname -m   # must print aarch64
```

### `as: unrecognized option` / Mach-O confusion

**Cause:** Running `make` on macOS host instead of inside Docker — host `as` targets
Darwin, not Linux ELF.  
**Fix:** Always use `./docker/phase1/run.sh make -C …`.

### `arithmetic FAIL`

**Cause:** Edited immediates or broke the compare chain.  
**Fix:** Re-check `mov`/`add`/`sub`/`ldr`/`str` against Section 5; rebuild with
`make clean all`.

### GDB: `Error disabling address space randomization: Operation not permitted`

```
warning: Error disabling address space randomization: Operation not permitted
```

**Cause:** Container lacks permission to change ASLR — warning only.  
**Fix:** Ignore for this lesson; register values are still valid.

### Context switch crashes / `Segmentation fault`

**Cause:** Stack not 16-byte aligned, or `struct context` layout mismatch vs
`switch.S` offsets.  
**Fix:** Keep `STACK_SIZE` and alignment attributes; do not reorder `struct context`
fields without updating every `str`/`ldr` offset in `switch.S`.

### Confusing `w0` and `x0`

**Pitfall:** `mov w0, #1` writes only 32 bits (often zero-extends into `x0`);
thinking they are different physical registers.  
**Reality:** Same register, different width views.

### Thinking Docker is "not QEMU"

**Note:** PRD accepts "QEMU or target." On Apple Silicon, Docker runs arm64
Linux natively (no instruction emulator). On x86 hosts, Docker uses emulation
under the hood. Either way you get a runnable AArch64 Linux userspace — the
acceptance bar for Phase 1.

---

## 11. Summary

- AArch64 gives you 31 general registers (`x0`–`x30`) plus SP; Linux syscalls use
  `x8` + `svc #0`.
- AAPCS64 splits caller-saved vs callee-saved — context switch saves the
  callee-saved set plus FP/LR/SP.
- You can now hand-trace basic data-processing and memory instructions and see
  two tasks share one CPU cooperatively.

Phase 2 moves from the architecture to the **RK3566 SoC** block diagram and
register map.

---

## 12. Exercises

1. **Hand-trace (≥5 instructions):** On paper, execute these and list X0–X4 after
   each line:

   ```
   mov x0, #20
   mov x1, #5
   add x2, x0, x1
   sub x3, x2, x1
   mov x4, x3
   ```

2. **Syscall IDs:** Change `hello.S` to print a second line with another `write`.
   Keep a single `exit`.

3. **Register roles:** Why must `switch_to` save `x19`–`x28` but not `x0`–`x7` for
   this cooperative demo?

4. **Extend context switch:** Add a `task_c` and round-robin A→B→C→A.

5. **GDB:** At `fill_regs_ready`, what is `x30`? How does it relate to `main`?

---

## 13. References

- AstraOS PRD — [`docs/PRD.md`](../PRD.md) Phase 1 row  
- [ARM Architecture Reference Manual (Armv8-A)](https://developer.arm.com/documentation/ddi0487/latest)  
- [Procedure Call Standard for the Arm 64-bit Architecture (AAPCS64)](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst)  
- [Linux AArch64 syscall table](https://github.com/torvalds/linux/blob/master/include/uapi/asm-generic/unistd.h)  
- Phase 0 lesson — [`00-computer-fundamentals.md`](00-computer-fundamentals.md)

---

## 14. Limitations / Future Improvements

- Userspace only — no EL1 exception levels, interrupts, or MMU setup on bare metal
- Context switch ignores FP/SIMD (`v0`–`v31`) and caller-saved GPRs
- Does not yet run on the Radxa ZERO 3W (board bring-up starts Phase 3–4)
- Future: QEMU system-mode virt machine, bare-metal `crt0`, and on-target static
  binaries once U-Boot/kernel path exists

---

*End of Lesson 01. Wait for Phase 1 confirmation before starting Phase 2.*
