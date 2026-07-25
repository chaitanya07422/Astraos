# Lesson 00 — Computer Fundamentals

**Phase:** 0  
**Hardware required:** None (host machine only)  
**Estimated time:** 4–8 hours  
**Prerequisites:** Comfortable reading Python; no embedded background assumed

---

## 1. Introduction

Before you touch a Radxa ZERO 3W, a Boot ROM, or a Linux kernel, you need a
shared vocabulary for what a computer *is* at the lowest levels you will care
about: numbers in binary and hexadecimal, registers, memory addresses, caches,
and the Memory Management Unit (MMU).

This lesson builds that vocabulary with three runnable simulators — not by
memorizing definitions. By the end you should be able to explain binary/hex,
registers, cache, and MMU in your own words, and prove it by running the demos
in `experiments/`.

AstraOS targets a Rockchip RK3566 (ARM Cortex-A55). Nothing in Phase 0 is
board-specific yet; Phase 1 starts mapping these ideas onto real AArch64.

---

## 2. Definitions

| Term | Definition |
|---|---|
| **Bit** | Smallest unit of information: 0 or 1. |
| **Byte** | 8 bits. The usual addressable unit in modern systems. |
| **Binary** | Base-2 numbering (`0b1010` = decimal 10). |
| **Hexadecimal (hex)** | Base-16 numbering (`0xA` = decimal 10). One hex digit = 4 bits (a nibble). |
| **Register** | A tiny, named storage slot *inside* the CPU, accessed in a single cycle. Far faster than RAM. |
| **RAM / memory** | Byte-addressable storage the CPU reads and writes by numeric address. |
| **Address** | An integer index into memory (e.g. `0x10` means "byte ten"). |
| **Little-endian** | Multi-byte values store the *least* significant byte at the lowest address. RK3566 / ARM follow this. |
| **Cache** | Small, fast memory that holds recently used data so the CPU avoids waiting on slower RAM. |
| **MMU** | Memory Management Unit — hardware that translates **virtual** addresses (what software uses) into **physical** addresses (where RAM actually lives). |
| **Page** | Fixed-size chunk of address space (commonly 4 KiB). Translation happens per page, not per byte. |
| **VPN / PFN** | Virtual Page Number / Physical Frame Number — the high bits of virtual / physical addresses. |
| **TLB** | Translation Lookaside Buffer — a cache of recent VPN→PFN translations. |
| **Page fault** | Exception when software accesses a virtual page with no valid mapping. |
| **PC** | Program Counter — register holding the address (or index) of the next instruction to fetch. |
| **ISA** | Instruction Set Architecture — the machine language a CPU understands. |

---

## 3. Architecture

A simplified picture of what Phase 0 models:

```
┌─────────────────────────────────────────────────────────┐
│                        CPU                              │
│  registers R0..Rn   PC   flags (e.g. ZERO)              │
│         │                                               │
│         ▼                                               │
│  ┌─────────────┐     ┌─────────────┐                    │
│  │    TLB      │────▶│ page table  │  (MMU)             │
│  │ (VPN→PFN    │ miss│  (in RAM)   │                    │
│  │  cache)     │     └──────┬──────┘                    │
│  └──────┬──────┘            │                           │
└─────────┼───────────────────┼───────────────────────────┘
          │ hit / after walk  │
          ▼                   ▼
     physical address ──▶  RAM (byte-addressable)
```

Software issues **virtual** addresses. The MMU (helped by the TLB) produces
**physical** addresses. The CPU then reads or writes RAM at that physical
location. Caches sit between CPU and RAM in real hardware; our MMU demo treats
the TLB as the concrete "cache of translations" you can observe.

---

## 4. Internal Workflow

### Numbers: binary and hex

Computers store everything as bits. Hex is a human-friendly shorthand: each hex
digit packs four bits.

| Decimal | Binary | Hex |
|---|---|---|
| 0 | `0000` | `0x0` |
| 10 | `1010` | `0xA` |
| 15 | `1111` | `0xF` |
| 16 | `0001 0000` | `0x10` |
| 255 | `1111 1111` | `0xFF` |

When you see a UART log address like `0x80080000`, you are already reading hex.

### Memory access

1. CPU presents an address and a width (8/16/32 bits).
2. On little-endian machines, a 32-bit store of `0x12345678` at `0x10` writes
   bytes `78 56 34 12` starting at `0x10`.
3. A dump of those bytes is how you verify what the machine actually stored.

### Address translation

1. Split virtual address into **VPN** (high bits) + **offset** (low 12 bits for
   4 KiB pages).
2. Look up VPN in the **TLB**. Hit → reuse PFN. Miss → walk the **page table**.
3. Physical address = `(PFN << 12) | offset`.
4. Unmapped VPN → **page fault**. Read-only page + write → **protection fault**.

### CPU instruction cycle

1. **Fetch** instruction at PC.
2. **Decode** opcode and operands.
3. **Execute** (touch registers and/or memory).
4. Advance PC (or branch), repeat until HALT.

---

## 5. Diagrams

### Virtual → physical (4 KiB pages)

```
Virtual address  0x1042
├──────── VPN=1 ────────┤├── offset=0x042 ──┤
        15...12                 11...0

Page table: VPN 1 → PFN 3

Physical address 0x3042
├──────── PFN=3 ────────┤├── offset=0x042 ──┤
```

Offset is copied unchanged. Only the high bits are translated.

### Fetch–decode–execute

```
   ┌──────┐    ┌────────┐    ┌─────────┐
   │Fetch │───▶│ Decode │───▶│ Execute │──┐
   └──▲───┘    └────────┘    └─────────┘  │
      │                                    │
      └──────────── PC update ◄────────────┘
```

---

## 6. Source Code

| Artifact | Path |
|---|---|
| Memory simulator | [`experiments/phase0-memory/memory_sim.py`](../../experiments/phase0-memory/memory_sim.py) |
| Address translation demo | [`experiments/phase0-address-translation/mmu_demo.py`](../../experiments/phase0-address-translation/mmu_demo.py) |
| CPU simulator | [`experiments/phase0-cpu/cpu_sim.py`](../../experiments/phase0-cpu/cpu_sim.py) |
| Sample ASM programs | [`experiments/phase0-cpu/programs/`](../../experiments/phase0-cpu/programs/) |

Each directory has a `README.md` and a `Makefile`.

---

## 7. Implementation

All three demos are pure Python 3.9+ — no cross-compiler, no board, no Docker
yet (Docker arrives when we need reproducible cross-compilation).

Design choices for teaching clarity:

- **Memory:** explicit `read8` / `write32` and a hex `dump`, so endianness is
  visible in the byte stream.
- **MMU:** 4 KiB pages, a software page table, and a 4-entry TLB so hit vs walk
  is printed on every access.
- **CPU:** an 8-register, 8-bit toy ISA with LOAD/STORE/ADD/branch — enough to
  see registers and PC without drowning in AArch64 encoding (Phase 1).

License: code is MIT; this lesson text is CC BY-SA 4.0 (see repo `LICENSE`).

---

## 8. Experiment

From the repository root (macOS or Linux):

```bash
# Confirm Python
python3 --version
# Expected: Python 3.9.x or newer
```

### Experiment A — Memory

```bash
make -C experiments/phase0-memory run
```

**Expected (excerpt):**

```
=== AstraOS Memory Simulator Demo ===
1) Binary ↔ hex ↔ decimal
     0  bin=00000000  hex=0x00
...
3) Little-endian 32-bit store of 0x12345678 at address 0x10
0010:  78 56 34 12 ...
   read32(0x10) = 0x12345678
   byte[0x10]=0x78 (low byte first = little-endian)
```

Optional REPL:

```bash
make -C experiments/phase0-memory repl
# then: write32 0x10 0xdeadbeef
#       dump 0x10 16
#       quit
```

### Experiment B — Address translation

```bash
make -C experiments/phase0-address-translation run
```

**Expected (excerpt):**

```
write8 → path=WALK, phys=0x3042, stored 0xAB
read8  → path=TLB, value=0xab
PermissionError: page fault: no valid mapping for VPN=0
PermissionError: protection fault: VPN=4 mapped read-only
```

### Experiment C — CPU

```bash
make -C experiments/phase0-cpu run
make -C experiments/phase0-cpu loop
```

**Expected:** demo prints `PRINT R3 = 12` and `mem[0x20] = 12`. The loop
program prints `3`, `2`, `1`, `0` then halts.

---

## 9. Result

On a reference run (Python 3.9.6, macOS):

| Demo | Result |
|---|---|
| Memory | Binary/hex table printed; LE store verified; OOB access raised `IndexError` |
| MMU | First access `WALK`, second `TLB`; page fault and protection fault raised as designed |
| CPU | `7+5=12` stored at `0x20`; countdown loop completed in 27 cycles |

Acceptance for Phase 0 (from the PRD roadmap): simulators **run** and are
**documented**; you can explain binary/hex, registers, cache, and MMU in your
own words (use the exercises below as a self-check).

---

## 10. Troubleshooting & Common Pitfalls

### `python3: command not found`

```
zsh: command not found: python3
```

**Cause:** Python 3 is not on your `PATH`.  
**Fix (macOS):** `xcode-select --install` then install Python from python.org, or
`brew install python`.  
**Fix (Linux):** `sudo apt install python3` (Debian/Ubuntu) or equivalent.

### `SyntaxError: unsupported operand type(s) for |: 'type' and 'NoneType'`

```
TypeError: unsupported operand type(s) for |
```

or on older Python:

```
TypeError: 'type' object is not subscriptable
```

**Cause:** These scripts use Python 3.9+ syntax (`list[str]`, `int | None`).  
**Fix:** Run with `python3 --version` ≥ 3.9. On some systems `python` is still
2.7 — always invoke `python3`.

### `make: python3 memory_sim.py --demo` fails with `No such file or directory`

```
make: *** No rule to make target 'run'.  Stop.
```

**Cause:** Wrong working directory, or you ran `make run` without `-C`.  
**Fix:**

```bash
cd experiments/phase0-memory && make run
# or from repo root:
make -C experiments/phase0-memory run
```

### `IndexError: address out of range: need [0x100..0x100] but memory is [0x0..0x3f]`

**Cause:** Demo memory is only 64 bytes; address `0x100` is intentionally
invalid.  
**Not a bug** if you saw this during the demo's step 4. In the REPL, stay within
`0x00..0xFF` (256-byte default).

### `PermissionError: page fault: no valid mapping for VPN=0`

**Cause:** You accessed a virtual address whose VPN was never `map`ped.  
**Fix:** In the REPL, `map 0 1` before `read 0x0`. In real OSes this fault is
how demand paging and segfaults begin — getting one here means the model is
working.

### `RuntimeError: exceeded max_cycles=1000 (possible infinite loop)`

**Cause:** A `JMP` / `BEQ` loop never reaches `HALT` (missing exit condition).  
**Fix:** Check `CMP`/`BEQ` logic; add `PRINT` traces; compare against
`programs/loop.asm`.

### Mixing up cache and TLB

**Pitfall:** Calling every fast structure "the cache."  
**Clarification:** Data caches store *bytes from RAM*. The TLB caches
*address translations*. Both are caches; they hold different things. This
lesson's MMU demo only models the TLB.

### Assuming hex dumps show integers left-to-right as written

**Pitfall:** Expecting `0x12345678` to appear as `12 34 56 78` in memory.  
**Reality on little-endian (including RK3566):** you will see `78 56 34 12`.
Always read multi-byte values with the correct endianness.

---

## 11. Summary

- Binary and hex are two views of the same bits; hex is how logs and addresses
  are usually written.
- Registers are the CPU's working set; RAM is large and addressed by integer
  locations; endianness decides byte order for multi-byte values.
- The MMU translates virtual→physical addresses per page; the TLB caches those
  translations; missing mappings cause page faults.
- A CPU repeatedly fetches, decodes, and executes instructions, updating the PC
  and registers — the same loop every higher layer (U-Boot, Linux) ultimately
  relies on.

You now have enough mental model to start talking about a real ARM64 CPU in
Phase 1.

---

## 12. Exercises

1. **Own words:** Without looking at this page, write 2–3 sentences each on
   binary/hex, registers, cache (including TLB vs data cache), and the MMU.
   Compare against Section 2.
2. **Endianness:** Using the memory REPL, store `0xAABBCCDD` at `0x08` and
   dump it. Predict the four bytes *before* running the command.
3. **TLB math:** Map three different VPNs, access each twice, and report the
   TLB hit rate from `stats`. Explain why the first access of each page misses.
4. **Extend the CPU:** Add a `NAND Rd, Ra, Rb` instruction (`Rd = ~(Ra & Rb) &
   0xFF`) and write a 4-instruction program that clears R0 using only `NAND`
   and `LI` if needed.
5. **Page math:** Virtual address `0x2ABC` — what are VPN and offset with 4 KiB
   pages? If VPN maps to PFN 9, what is the physical address?

---

## 13. References

- AstraOS PRD — [`docs/PRD.md`](../PRD.md) (Phase 0 roadmap row, Documentation Standard)
- Patterson & Hennessy, *Computer Organization and Design* (ARM or RISC-V edition) — chapters on arithmetic, memory hierarchy, and virtual memory
- [Linux kernel docs: Page Table Management](https://docs.kernel.org/mm/page_tables.html) (preview of where this goes)
- [Little-endian explanation (Wikipedia)](https://en.wikipedia.org/wiki/Endianness)

---

## 14. Limitations / Future Improvements

- Simulators are intentionally tiny (8-bit CPU, 16-page MMU). They teach
  vocabulary, not RK3566 microarchitecture.
- No data-cache timing model — only a TLB hit/miss counter.
- No multi-level page tables, ASID, or permission bits beyond R/W.
- CPU ISA is not AArch64; Phase 1 replaces it with real ARM64 assembly on QEMU
  or the board.
- Future: optional Jupyter notebooks, a shared `experiments/phase0-common`
  package, and golden-output tests in CI once Phase 0 documentation is public.

---

*End of Lesson 00. When Phase 0 exit criteria are confirmed, proceed to Phase 1
(ARM64 Architecture) only after the project owner signs off.*
