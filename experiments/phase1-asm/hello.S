// AstraOS Phase 1 — minimal AArch64 "hello" via Linux write syscall.
// Trace targets: mov, adr/ldr literal, mov (wide), svc, ret

.section .rodata
msg:
    .ascii "AstraOS Phase 1: hello from AArch64\n"
msg_len = . - msg

.section .text
.global _start
_start:
    // write(1, msg, msg_len)  — Linux AArch64: syscall #64 in x8
    mov     x0, #1              // fd = stdout
    adr     x1, msg             // buf
    mov     x2, #msg_len        // count
    mov     x8, #64             // __NR_write
    svc     #0

    // exit(0)  — syscall #93
    mov     x0, #0
    mov     x8, #93             // __NR_exit
    svc     #0
