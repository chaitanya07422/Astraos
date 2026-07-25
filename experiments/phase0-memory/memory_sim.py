#!/usr/bin/env python3
"""
AstraOS Phase 0 — Memory Simulator

Byte-addressable RAM with little-endian multi-byte loads/stores,
hex dumps, and binary/hex conversion helpers.

Usage:
  python3 memory_sim.py          # run built-in demo
  python3 memory_sim.py --demo   # same
  python3 memory_sim.py --repl   # interactive REPL
"""

from __future__ import annotations

import argparse
import sys
from typing import List


class Memory:
    """Simple byte-addressable memory (little-endian for multi-byte access)."""

    def __init__(self, size: int = 256) -> None:
        if size <= 0:
            raise ValueError(f"size must be positive, got {size}")
        self.size = size
        self._data = bytearray(size)

    def _check(self, addr: int, width: int) -> None:
        if addr < 0 or addr + width > self.size:
            raise IndexError(
                f"address out of range: need [{addr:#x}..{addr + width - 1:#x}] "
                f"but memory is [0x0..{self.size - 1:#x}]"
            )

    def write8(self, addr: int, value: int) -> None:
        self._check(addr, 1)
        self._data[addr] = value & 0xFF

    def read8(self, addr: int) -> int:
        self._check(addr, 1)
        return self._data[addr]

    def write16(self, addr: int, value: int) -> None:
        """Store 16-bit value little-endian (low byte at addr)."""
        self._check(addr, 2)
        value &= 0xFFFF
        self._data[addr] = value & 0xFF
        self._data[addr + 1] = (value >> 8) & 0xFF

    def read16(self, addr: int) -> int:
        self._check(addr, 2)
        return self._data[addr] | (self._data[addr + 1] << 8)

    def write32(self, addr: int, value: int) -> None:
        """Store 32-bit value little-endian."""
        self._check(addr, 4)
        value &= 0xFFFFFFFF
        for i in range(4):
            self._data[addr + i] = (value >> (8 * i)) & 0xFF

    def read32(self, addr: int) -> int:
        self._check(addr, 4)
        result = 0
        for i in range(4):
            result |= self._data[addr + i] << (8 * i)
        return result

    def dump(self, start: int = 0, length: int | None = None) -> str:
        """Return a classic hex dump (16 bytes per line)."""
        if length is None:
            length = self.size - start
        if length < 0:
            raise ValueError("length must be non-negative")
        if length > 0:
            self._check(start, 1)
        end = min(start + length, self.size)
        lines: List[str] = []
        addr = start
        while addr < end:
            chunk = self._data[addr : min(addr + 16, end)]
            hex_part = " ".join(f"{b:02x}" for b in chunk)
            ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            lines.append(f"{addr:04x}:  {hex_part:<47}  |{ascii_part}|")
            addr += 16
        return "\n".join(lines)


def to_binary(n: int, bits: int = 8) -> str:
    return format(n & ((1 << bits) - 1), f"0{bits}b")


def to_hex(n: int, width: int = 2) -> str:
    return f"0x{n:0{width}x}"


def demo() -> int:
    print("=== AstraOS Memory Simulator Demo ===\n")

    print("1) Binary ↔ hex ↔ decimal")
    for n in (0, 1, 10, 15, 16, 255):
        print(f"   {n:3d}  bin={to_binary(n)}  hex={to_hex(n)}")
    print()

    mem = Memory(64)
    print("2) Write bytes, then dump")
    mem.write8(0x00, 0x41)  # 'A'
    mem.write8(0x01, 0x42)  # 'B'
    mem.write8(0x02, 0x43)  # 'C'
    print(mem.dump(0, 16))
    print()

    print("3) Little-endian 32-bit store of 0x12345678 at address 0x10")
    mem.write32(0x10, 0x12345678)
    print(mem.dump(0x10, 16))
    print(f"   read32(0x10) = {to_hex(mem.read32(0x10), 8)}")
    print(f"   byte[0x10]={to_hex(mem.read8(0x10))} (low byte first = little-endian)")
    print(f"   byte[0x13]={to_hex(mem.read8(0x13))} (high byte last)")
    print()

    print("4) Out-of-range access (expected error)")
    try:
        mem.read8(0x100)
    except IndexError as exc:
        print(f"   IndexError: {exc}")
    print()
    print("Demo complete.")
    return 0


def repl() -> int:
    mem = Memory(256)
    print("Memory REPL — commands: write8 ADDR VAL | read8 ADDR | write32 ADDR VAL")
    print("               read32 ADDR | dump [START [LEN]] | quit")
    print("Addresses and values accept 0x hex or decimal.\n")
    while True:
        try:
            line = input("mem> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not line:
            continue
        parts = line.split()
        cmd = parts[0].lower()
        try:
            if cmd in ("quit", "q", "exit"):
                return 0
            if cmd == "write8" and len(parts) == 3:
                mem.write8(int(parts[1], 0), int(parts[2], 0))
            elif cmd == "read8" and len(parts) == 2:
                print(to_hex(mem.read8(int(parts[1], 0))))
            elif cmd == "write32" and len(parts) == 3:
                mem.write32(int(parts[1], 0), int(parts[2], 0))
            elif cmd == "read32" and len(parts) == 2:
                print(to_hex(mem.read32(int(parts[1], 0)), 8))
            elif cmd == "dump":
                start = int(parts[1], 0) if len(parts) > 1 else 0
                length = int(parts[2], 0) if len(parts) > 2 else 64
                print(mem.dump(start, length))
            else:
                print("unknown command — try: write8 0x10 0xff | dump 0 32 | quit")
        except (ValueError, IndexError) as exc:
            print(f"error: {exc}")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AstraOS Phase 0 memory simulator")
    parser.add_argument("--demo", action="store_true", help="run built-in demo (default)")
    parser.add_argument("--repl", action="store_true", help="interactive REPL")
    args = parser.parse_args(argv)
    if args.repl:
        return repl()
    return demo()


if __name__ == "__main__":
    sys.exit(main())
