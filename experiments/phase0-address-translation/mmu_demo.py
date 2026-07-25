#!/usr/bin/env python3
"""
AstraOS Phase 0 — Address Translation (MMU) Demo

Simulates a tiny Memory Management Unit (MMU): virtual → physical address
translation via a page table, with a small Translation Lookaside Buffer (TLB)
cache in front.

Page size: 4 KiB (12 offset bits)
VPN / PFN: remaining high bits of a 16-bit address space (demo-sized)

Usage:
  python3 mmu_demo.py
  python3 mmu_demo.py --repl
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


PAGE_SHIFT = 12  # 4 KiB pages
PAGE_SIZE = 1 << PAGE_SHIFT
VPN_BITS = 4  # demo: 16 virtual pages
PFN_BITS = 4  # demo: 16 physical frames


@dataclass
class PageTableEntry:
    pfn: int
    valid: bool = True
    writable: bool = True


class TLB:
    """Tiny fully-associative TLB (cache of recent VPN→PFN translations)."""

    def __init__(self, capacity: int = 4) -> None:
        self.capacity = capacity
        self._entries: Dict[int, int] = {}  # vpn -> pfn
        self.hits = 0
        self.misses = 0

    def lookup(self, vpn: int) -> Optional[int]:
        if vpn in self._entries:
            self.hits += 1
            return self._entries[vpn]
        self.misses += 1
        return None

    def insert(self, vpn: int, pfn: int) -> None:
        if vpn not in self._entries and len(self._entries) >= self.capacity:
            # Evict an arbitrary entry (FIFO-ish via dict order)
            oldest = next(iter(self._entries))
            del self._entries[oldest]
        self._entries[vpn] = pfn

    def invalidate(self) -> None:
        self._entries.clear()

    def stats(self) -> str:
        total = self.hits + self.misses
        rate = (100.0 * self.hits / total) if total else 0.0
        return f"TLB hits={self.hits} misses={self.misses} hit_rate={rate:.1f}%"


class MMU:
    def __init__(self) -> None:
        self.page_table: Dict[int, PageTableEntry] = {}
        self.tlb = TLB(capacity=4)
        self.phys_mem = bytearray(PAGE_SIZE * (1 << PFN_BITS))

    def map_page(self, vpn: int, pfn: int, writable: bool = True) -> None:
        if not (0 <= vpn < (1 << VPN_BITS)):
            raise ValueError(f"VPN out of range: {vpn}")
        if not (0 <= pfn < (1 << PFN_BITS)):
            raise ValueError(f"PFN out of range: {pfn}")
        self.page_table[vpn] = PageTableEntry(pfn=pfn, valid=True, writable=writable)
        self.tlb.invalidate()  # mapping change → flush TLB

    def translate(self, virt: int, write: bool = False) -> Tuple[int, str]:
        """Return (phys_addr, path) where path is 'TLB' or 'WALK'."""
        vpn = virt >> PAGE_SHIFT
        offset = virt & (PAGE_SIZE - 1)

        cached = self.tlb.lookup(vpn)
        if cached is not None:
            pfn = cached
            path = "TLB"
        else:
            pte = self.page_table.get(vpn)
            if pte is None or not pte.valid:
                raise PermissionError(
                    f"page fault: no valid mapping for VPN={vpn} "
                    f"(virt={virt:#x})"
                )
            pfn = pte.pfn
            self.tlb.insert(vpn, pfn)
            path = "WALK"

        pte = self.page_table.get(vpn)
        if write and pte is not None and not pte.writable:
            raise PermissionError(
                f"protection fault: VPN={vpn} mapped read-only (virt={virt:#x})"
            )

        phys = (pfn << PAGE_SHIFT) | offset
        return phys, path

    def write8(self, virt: int, value: int) -> str:
        phys, path = self.translate(virt, write=True)
        self.phys_mem[phys] = value & 0xFF
        return path

    def read8(self, virt: int) -> Tuple[int, str]:
        phys, path = self.translate(virt, write=False)
        return self.phys_mem[phys], path


def split_addr(virt: int) -> str:
    vpn = virt >> PAGE_SHIFT
    offset = virt & (PAGE_SIZE - 1)
    return f"virt={virt:#06x} → VPN={vpn} offset={offset:#05x}"


def demo() -> int:
    print("=== AstraOS Address Translation (MMU) Demo ===\n")
    print(f"Page size = {PAGE_SIZE} bytes ({PAGE_SIZE // 1024} KiB)")
    print(f"Virtual pages = {1 << VPN_BITS}, physical frames = {1 << PFN_BITS}\n")

    mmu = MMU()

    print("1) Map VPN 1 → PFN 3, VPN 2 → PFN 5")
    mmu.map_page(1, 3)
    mmu.map_page(2, 5)
    print("   page_table: {", end="")
    print(", ".join(f"VPN{v}→PFN{e.pfn}" for v, e in sorted(mmu.page_table.items())), end="")
    print("}\n")

    v1 = (1 << PAGE_SHIFT) | 0x42  # VPN1 + offset 0x42
    print(f"2) First access {split_addr(v1)} (expect page-table WALK, TLB miss)")
    path = mmu.write8(v1, 0xAB)
    # phys = PFN 3, same offset (do not call translate again — that would add a TLB hit)
    phys = (3 << PAGE_SHIFT) | (v1 & (PAGE_SIZE - 1))
    print(f"   write8 → path={path}, phys={phys:#06x}, stored 0xAB")

    print(f"3) Second access same page (expect TLB hit)")
    val, path = mmu.read8(v1)
    print(f"   read8  → path={path}, value={val:#04x}")
    print(f"   {mmu.tlb.stats()}\n")

    print("4) Unmapped access (expect page fault)")
    try:
        mmu.read8(0x0000)  # VPN 0 not mapped
    except PermissionError as exc:
        print(f"   PermissionError: {exc}\n")

    print("5) Read-only mapping protection fault")
    mmu.map_page(4, 7, writable=False)
    try:
        mmu.write8((4 << PAGE_SHIFT), 0xFF)
    except PermissionError as exc:
        print(f"   PermissionError: {exc}\n")

    print(f"Final {mmu.tlb.stats()}")
    print("Demo complete.")
    return 0


def repl() -> int:
    mmu = MMU()
    print("MMU REPL — map VPN PFN [ro] | read VIRT | write VIRT VAL | translate VIRT | stats | quit")
    while True:
        try:
            line = input("mmu> ").strip()
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
            if cmd == "map" and len(parts) >= 3:
                ro = len(parts) > 3 and parts[3] == "ro"
                mmu.map_page(int(parts[1], 0), int(parts[2], 0), writable=not ro)
                print("ok")
            elif cmd == "read" and len(parts) == 2:
                val, path = mmu.read8(int(parts[1], 0))
                print(f"value={val:#04x} path={path}")
            elif cmd == "write" and len(parts) == 3:
                path = mmu.write8(int(parts[1], 0), int(parts[2], 0))
                print(f"ok path={path}")
            elif cmd == "translate" and len(parts) == 2:
                virt = int(parts[1], 0)
                phys, path = mmu.translate(virt)
                print(f"{split_addr(virt)} → phys={phys:#06x} via {path}")
            elif cmd == "stats":
                print(mmu.tlb.stats())
            else:
                print("unknown — try: map 1 3 | write 0x1042 | write 0x1042 0xab | quit")
        except (ValueError, PermissionError, IndexError) as exc:
            print(f"error: {exc}")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AstraOS Phase 0 MMU demo")
    parser.add_argument("--repl", action="store_true")
    args = parser.parse_args(argv)
    if args.repl:
        return repl()
    return demo()


if __name__ == "__main__":
    sys.exit(main())
