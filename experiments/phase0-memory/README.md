# AstraOS Phase 0 — Memory Simulator

Byte-addressable RAM with little-endian multi-byte access, hex dumps, and
binary/hex helpers. See the Phase 0 lesson for full context.

## Requirements

- Python 3.9+

## Build / run

```bash
make run
# or
python3 memory_sim.py
```

Interactive REPL:

```bash
make repl
```

## Expected demo output (excerpt)

```
=== AstraOS Memory Simulator Demo ===

1) Binary ↔ hex ↔ decimal
     0  bin=00000000  hex=0x00
     1  bin=00000001  hex=0x01
    ...
3) Little-endian 32-bit store of 0x12345678 at address 0x10
   read32(0x10) = 0x12345678
   byte[0x10]=0x78 (low byte first = little-endian)
```

## Configuration

Default memory size is 64 bytes in demo mode and 256 bytes in REPL.
Edit `Memory(size=...)` in `memory_sim.py` to change.

## Limitations

- No cache model (see address-translation demo for a simple TLB)
- No permissions / MMU (that is the next experiment)
- Educational only — not a cycle-accurate DRAM model
