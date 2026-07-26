/* AstraOS Phase 1 — register inspection helper (C side). */
#include <stdio.h>
#include <stdint.h>

/* Filled by fill_regs() in registers.S — distinctive constants. */
struct gpr_snapshot {
    uint64_t x[31]; /* x0..x30 */
    uint64_t sp;
};

void fill_regs(struct gpr_snapshot *out);

int main(void)
{
    struct gpr_snapshot s = {0};
    fill_regs(&s);

    printf("=== AArch64 GPR snapshot (after fill_regs) ===\n");
    for (int i = 0; i < 31; i++) {
        printf("  x%-2d = 0x%016llx  (%llu)\n",
               i,
               (unsigned long long)s.x[i],
               (unsigned long long)s.x[i]);
    }
    printf("  sp  = 0x%016llx\n", (unsigned long long)s.sp);
    printf("\nExpected highlights:\n");
    printf("  x0  = 0xA0A0A0A0A0A0A0A0\n");
    printf("  x1  = 0x0000000000000001\n");
    printf("  x19 = 0x0000000000000013  (callee-saved sample)\n");
    printf("  x30 (LR) preserved across fill_regs return\n");
    return 0;
}
