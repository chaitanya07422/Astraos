# Phase 3 — Boot log capture

Goal: capture a **real** power-on → shell UART log from a Radxa ZERO 3W, then
annotate every boot stage.

## Before you start

1. Flash the **vendor** image per [`images/README.md`](../../images/README.md)
   (official Radxa `.img`, not a fake AstraOS release).
2. Wire UART (pins 8/10/6, **1500000** 8N1).
3. Capture the log into this folder.

## Drop your log here

```text
experiments/phase3-boot/logs/power-on-to-shell.raw.txt
```

After that file exists, we will produce:

- `logs/power-on-to-shell.annotated.md` — stage-by-stage notes  
- Modified boot-command documentation (U-Boot env change)  
- Lesson 03  

## Status

| Item | Status |
|---|---|
| Vendor flash guide | See `images/README.md` |
| Raw UART log | **Waiting on your capture** |
| Annotated log | Blocked on raw log |
| Modified boot commands | Blocked on working U-Boot prompt |
| Phase 3 exit criteria | **Not met yet** |
