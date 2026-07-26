// AstraOS Phase 1 — fill distinctive GPR values, spill into a C struct.
// AAPCS64: x0 = &snapshot on entry. Must preserve x19–x28, x29, x30.

.section .text
.global fill_regs
.type fill_regs, %function
fill_regs:
    stp     x29, x30, [sp, #-32]!
    mov     x29, sp
    stp     x19, x20, [sp, #16]

    mov     x9, x0                  // x9 = &snapshot (keep pointer)

    // Distinctive caller-saved / argument values
    movz    x0, #0xA0A0
    movk    x0, #0xA0A0, lsl #16
    movk    x0, #0xA0A0, lsl #32
    movk    x0, #0xA0A0, lsl #48
    mov     x1, #1
    mov     x2, #2
    mov     x3, #3
    mov     x4, #4
    mov     x5, #5
    mov     x6, #6
    mov     x7, #7
    mov     x8, #8
    mov     x10, #10
    mov     x11, #11
    mov     x12, #12
    mov     x13, #13
    mov     x14, #14
    mov     x15, #15
    mov     x16, #16
    mov     x17, #17
    // x18 left unchanged (platform register on some ABIs)

    mov     x19, #0x13              // callee-saved samples
    mov     x20, #0x14

    str     x0,  [x9, #(0 * 8)]
    str     x1,  [x9, #(1 * 8)]
    str     x2,  [x9, #(2 * 8)]
    str     x3,  [x9, #(3 * 8)]
    str     x4,  [x9, #(4 * 8)]
    str     x5,  [x9, #(5 * 8)]
    str     x6,  [x9, #(6 * 8)]
    str     x7,  [x9, #(7 * 8)]
    str     x8,  [x9, #(8 * 8)]
    str     x9,  [x9, #(9 * 8)]     // pointer value itself
    str     x10, [x9, #(10 * 8)]
    str     x11, [x9, #(11 * 8)]
    str     x12, [x9, #(12 * 8)]
    str     x13, [x9, #(13 * 8)]
    str     x14, [x9, #(14 * 8)]
    str     x15, [x9, #(15 * 8)]
    str     x16, [x9, #(16 * 8)]
    str     x17, [x9, #(17 * 8)]
    str     x18, [x9, #(18 * 8)]
    str     x19, [x9, #(19 * 8)]
    str     x20, [x9, #(20 * 8)]
    str     x21, [x9, #(21 * 8)]
    str     x22, [x9, #(22 * 8)]
    str     x23, [x9, #(23 * 8)]
    str     x24, [x9, #(24 * 8)]
    str     x25, [x9, #(25 * 8)]
    str     x26, [x9, #(26 * 8)]
    str     x27, [x9, #(27 * 8)]
    str     x28, [x9, #(28 * 8)]
    str     x29, [x9, #(29 * 8)]
    str     x30, [x9, #(30 * 8)]

    mov     x10, sp
    str     x10, [x9, #(31 * 8)]    // snapshot.sp

    // GDB breakpoint target — regs still hold demo values (before restore)
.global fill_regs_ready
fill_regs_ready:
    nop

    ldp     x19, x20, [sp, #16]
    ldp     x29, x30, [sp], #32
    ret
.size fill_regs, .-fill_regs
