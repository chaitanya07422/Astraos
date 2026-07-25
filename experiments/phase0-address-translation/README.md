# AstraOS Phase 0 — Address Translation (MMU) Demo

Simulates virtual→physical translation with a page table and a small TLB
(Translation Lookaside Buffer) cache.

## Requirements

- Python 3.9+

## Build / run

```bash
make run
# or
python3 mmu_demo.py
```

## Expected demo output (excerpt)

```
=== AstraOS Address Translation (MMU) Demo ===
Page size = 4096 bytes (4 KiB)
...
2) First access ... (expect page-table WALK, TLB miss)
   write8 → path=WALK, ...
3) Second access same page (expect TLB hit)
   read8  → path=TLB, value=0xab
4) Unmapped access (expect page fault)
   PermissionError: page fault: no valid mapping for VPN=0 ...
```

## Key ideas

| Term | Meaning in this demo |
|---|---|
| VPN | Virtual Page Number (high bits of virtual address) |
| PFN | Physical Frame Number (high bits of physical address) |
| Offset | Low 12 bits — same in virtual and physical address |
| TLB | Cache of recent VPN→PFN translations |
| Page fault | Access to an unmapped VPN |

## Limitations

- Fixed 4 KiB pages, tiny 16-page address space (teaching size)
- Fully-associative TLB with naive eviction — not modeling real ARM MMU levels
- No multi-level page tables (real AArch64 uses multi-level tables)
