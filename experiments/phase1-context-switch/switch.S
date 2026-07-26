// AstraOS Phase 1 — cooperative context switch (AArch64)
// void switch_to(struct context *prev, struct context *next);
//   x0 = prev, x1 = next
//
// struct context layout (8-byte fields):
//   0:x19 8:x20 16:x21 24:x22 32:x23 40:x24 48:x25 56:x26
//   64:x27 72:x28 80:x29 88:x30 96:sp

.section .text
.global switch_to
.type switch_to, %function
switch_to:
    // Save callee-saved regs + FP/LR into *prev
    str     x19, [x0, #0]
    str     x20, [x0, #8]
    str     x21, [x0, #16]
    str     x22, [x0, #24]
    str     x23, [x0, #32]
    str     x24, [x0, #40]
    str     x25, [x0, #48]
    str     x26, [x0, #56]
    str     x27, [x0, #64]
    str     x28, [x0, #72]
    str     x29, [x0, #80]
    str     x30, [x0, #88]
    mov     x2, sp
    str     x2,  [x0, #96]

    // Restore from *next
    ldr     x19, [x1, #0]
    ldr     x20, [x1, #8]
    ldr     x21, [x1, #16]
    ldr     x22, [x1, #24]
    ldr     x23, [x1, #32]
    ldr     x24, [x1, #40]
    ldr     x25, [x1, #48]
    ldr     x26, [x1, #56]
    ldr     x27, [x1, #64]
    ldr     x28, [x1, #72]
    ldr     x29, [x1, #80]
    ldr     x30, [x1, #88]
    ldr     x2,  [x1, #96]
    mov     sp, x2

    ret                             // jump to next's saved LR / entry
.size switch_to, .-switch_to
