#!/usr/bin/env python3
"""
AstraOS Phase 0 — Simple CPU Simulator

A tiny register machine that demonstrates:
  - general-purpose registers
  - program counter (PC)
  - fetch → decode → execute loop
  - load/store against byte-addressable memory

Instruction set (one instruction per line):

  LOAD  Rd, addr     ; Rd = mem[addr]          (8-bit)
  STORE Rs, addr     ; mem[addr] = Rs          (8-bit)
  LI    Rd, imm      ; Rd = imm                (load immediate)
  ADD   Rd, Ra, Rb   ; Rd = (Ra + Rb) & 0xFF
  SUB   Rd, Ra, Rb   ; Rd = (Ra - Rb) & 0xFF
  CMP   Ra, Rb       ; set ZERO flag if Ra == Rb
  BEQ   label        ; branch if ZERO
  JMP   label        ; unconditional jump
  PRINT Rs           ; print register value
  HALT               ; stop

Usage:
  python3 cpu_sim.py
  python3 cpu_sim.py programs/add.asm
  python3 cpu_sim.py --trace programs/loop.asm
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


NUM_REGS = 8


class CPU:
    def __init__(self, mem_size: int = 256) -> None:
        self.regs = [0] * NUM_REGS
        self.pc = 0
        self.zero = False
        self.halted = False
        self.mem = bytearray(mem_size)
        self.program: List[Tuple[str, List[str]]] = []
        self.labels: Dict[str, int] = {}
        self.cycles = 0

    def load_program(self, source: str) -> None:
        self.program = []
        self.labels = {}
        for raw in source.splitlines():
            line = raw.split(";")[0].strip()
            if not line:
                continue
            if line.endswith(":"):
                label = line[:-1].strip()
                if not label:
                    raise ValueError(f"empty label in: {raw!r}")
                self.labels[label] = len(self.program)
                continue
            parts = line.replace(",", " ").split()
            op, args = parts[0].upper(), parts[1:]
            self.program.append((op, args))

    def _reg(self, token: str) -> int:
        token = token.upper()
        if not token.startswith("R") or not token[1:].isdigit():
            raise ValueError(f"expected register like R0, got {token}")
        idx = int(token[1:])
        if not (0 <= idx < NUM_REGS):
            raise ValueError(f"register out of range: {token}")
        return idx

    def _imm(self, token: str) -> int:
        return int(token, 0) & 0xFF

    def _addr(self, token: str) -> int:
        addr = int(token, 0)
        if not (0 <= addr < len(self.mem)):
            raise IndexError(f"memory address out of range: {addr:#x}")
        return addr

    def _target(self, token: str) -> int:
        if token in self.labels:
            return self.labels[token]
        # numeric PC target
        return int(token, 0)

    def step(self) -> str:
        if self.halted:
            return "HALTED"
        if not (0 <= self.pc < len(self.program)):
            raise RuntimeError(f"PC out of range: {self.pc}")

        op, args = self.program[self.pc]
        trace = f"PC={self.pc:02d} {op} {' '.join(args)}"
        self.pc += 1
        self.cycles += 1

        if op == "LI":
            rd, imm = self._reg(args[0]), self._imm(args[1])
            self.regs[rd] = imm
        elif op == "LOAD":
            rd, addr = self._reg(args[0]), self._addr(args[1])
            self.regs[rd] = self.mem[addr]
        elif op == "STORE":
            rs, addr = self._reg(args[0]), self._addr(args[1])
            self.mem[addr] = self.regs[rs] & 0xFF
        elif op == "ADD":
            rd, ra, rb = self._reg(args[0]), self._reg(args[1]), self._reg(args[2])
            self.regs[rd] = (self.regs[ra] + self.regs[rb]) & 0xFF
        elif op == "SUB":
            rd, ra, rb = self._reg(args[0]), self._reg(args[1]), self._reg(args[2])
            self.regs[rd] = (self.regs[ra] - self.regs[rb]) & 0xFF
        elif op == "CMP":
            ra, rb = self._reg(args[0]), self._reg(args[1])
            self.zero = self.regs[ra] == self.regs[rb]
            trace += f"  ; Z={int(self.zero)}"
        elif op == "BEQ":
            if self.zero:
                self.pc = self._target(args[0])
                trace += "  ; taken"
            else:
                trace += "  ; not taken"
        elif op == "JMP":
            self.pc = self._target(args[0])
        elif op == "PRINT":
            rs = self._reg(args[0])
            print(f"  PRINT R{rs} = {self.regs[rs]} (0x{self.regs[rs]:02x})")
        elif op == "HALT":
            self.halted = True
            trace += "  ; stop"
        else:
            raise ValueError(f"unknown opcode: {op}")

        return trace

    def run(self, trace: bool = False, max_cycles: int = 1000) -> None:
        while not self.halted:
            if self.cycles >= max_cycles:
                raise RuntimeError(f"exceeded max_cycles={max_cycles} (possible infinite loop)")
            line = self.step()
            if trace:
                regs = " ".join(f"R{i}={self.regs[i]}" for i in range(NUM_REGS))
                print(f"{line:40s} | {regs}")

    def dump_state(self) -> str:
        regs = ", ".join(f"R{i}={self.regs[i]}" for i in range(NUM_REGS))
        return (
            f"PC={self.pc} Z={int(self.zero)} halted={self.halted} cycles={self.cycles}\n"
            f"regs: {regs}"
        )


DEFAULT_PROGRAM = """\
; Add 7 + 5, store result at mem[0x20], print it
    LI    R1, 7
    LI    R2, 5
    ADD   R3, R1, R2
    STORE R3, 0x20
    PRINT R3
    HALT
"""


def demo() -> int:
    print("=== AstraOS Simple CPU Simulator Demo ===\n")
    print("Program:\n")
    for line in DEFAULT_PROGRAM.strip().splitlines():
        print(f"  {line}")
    print()

    cpu = CPU()
    cpu.load_program(DEFAULT_PROGRAM)
    print("Trace (fetch → decode → execute):\n")
    cpu.run(trace=True)
    print()
    print(cpu.dump_state())
    print(f"mem[0x20] = {cpu.mem[0x20]} (expected 12)")
    print("Demo complete.")
    return 0


def run_file(path: Path, trace: bool) -> int:
    source = path.read_text()
    cpu = CPU()
    cpu.load_program(source)
    cpu.run(trace=trace)
    print(cpu.dump_state())
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="AstraOS Phase 0 CPU simulator")
    parser.add_argument("program", nargs="?", help="path to .asm program")
    parser.add_argument("--trace", action="store_true", help="print each instruction")
    args = parser.parse_args(argv)
    if args.program:
        return run_file(Path(args.program), trace=args.trace or True)
    return demo()


if __name__ == "__main__":
    sys.exit(main())
