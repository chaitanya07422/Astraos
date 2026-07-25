# AstraOS Phase 0 — Simple CPU Simulator

A tiny register machine showing registers, the program counter (PC), and the
fetch → decode → execute loop.

## Requirements

- Python 3.9+

## Build / run

```bash
make run
# or
python3 cpu_sim.py
```

Run a sample program with a full trace:

```bash
make loop
# or
python3 cpu_sim.py --trace programs/loop.asm
```

## Instruction set

| Opcode | Form | Meaning |
|---|---|---|
| LI | `LI Rd, imm` | Rd = imm |
| LOAD | `LOAD Rd, addr` | Rd = mem[addr] |
| STORE | `STORE Rs, addr` | mem[addr] = Rs |
| ADD / SUB | `ADD Rd, Ra, Rb` | Rd = Ra ± Rb (8-bit) |
| CMP | `CMP Ra, Rb` | set ZERO if equal |
| BEQ / JMP | `BEQ label` | conditional / unconditional branch |
| PRINT | `PRINT Rs` | print register |
| HALT | `HALT` | stop |

## Expected demo output (excerpt)

```
=== AstraOS Simple CPU Simulator Demo ===
...
PC=00 LI R1 7                              | R0=0 R1=7 R2=0 ...
PC=02 ADD R3 R1 R2                         | R0=0 R1=7 R2=5 R3=12 ...
  PRINT R3 = 12 (0x0c)
mem[0x20] = 12 (expected 12)
```

## Limitations

- 8-bit datapath, 8 registers, no stack, no interrupts
- Not ARM/AArch64 — Phase 1 covers real ARM64 assembly
- Labels must appear before use in forward-reference-sensitive tools; here labels
  are collected in a first pass over the file so forward branches work
