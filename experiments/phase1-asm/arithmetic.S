// AstraOS Phase 1 — arithmetic + load/store for hand-tracing.
// Expected final values (verify with gdb or the printed line):
//   x2 = 13   (10 + 3)
//   x3 = 7    (10 - 3)
//   x4 = 42   (loaded from .data)
//   [result]  = 13 (stored)

.section .data
value:
    .quad   42
result:
    .quad   0

.section .rodata
ok_msg:
    .ascii "arithmetic OK: x2=13 x3=7 x4=42 result=13\n"
ok_len = . - ok_msg
bad_msg:
    .ascii "arithmetic FAIL\n"
bad_len = . - bad_msg

.section .text
.global _start
_start:
    mov     x0, #10
    mov     x1, #3
    add     x2, x0, x1          // x2 = 13
    sub     x3, x0, x1          // x3 = 7

    adr     x5, value
    ldr     x4, [x5]            // x4 = 42

    adr     x5, result
    str     x2, [x5]            // mem[result] = 13
    ldr     x6, [x5]            // x6 = 13

    // Check: x2==13, x3==7, x4==42, x6==13
    cmp     x2, #13
    b.ne    fail
    cmp     x3, #7
    b.ne    fail
    cmp     x4, #42
    b.ne    fail
    cmp     x6, #13
    b.ne    fail

    mov     x0, #1
    adr     x1, ok_msg
    mov     x2, #ok_len
    mov     x8, #64
    svc     #0
    b       exit

fail:
    mov     x0, #1
    adr     x1, bad_msg
    mov     x2, #bad_len
    mov     x8, #64
    svc     #0
    mov     x0, #1
    mov     x8, #93
    svc     #0

exit:
    mov     x0, #0
    mov     x8, #93
    svc     #0
