/* AstraOS Phase 1 — cooperative context-switch demo (C side). */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

#define STACK_SIZE 8192

/*
 * Callee-saved GPRs + FP + LR + SP.
 * Layout must match switch_to in switch.S.
 */
struct context {
    uint64_t x19, x20, x21, x22, x23, x24, x25, x26, x27, x28;
    uint64_t x29; /* FP */
    uint64_t x30; /* LR / resume PC */
    uint64_t sp;
};

void switch_to(struct context *prev, struct context *next);

static struct context main_ctx;
static struct context task_a_ctx;
static struct context task_b_ctx;
static uint8_t stack_a[STACK_SIZE] __attribute__((aligned(16)));
static uint8_t stack_b[STACK_SIZE] __attribute__((aligned(16)));

static void task_a(void)
{
    for (int i = 1; i <= 3; i++) {
        printf("  [task A] slice %d\n", i);
        switch_to(&task_a_ctx, &task_b_ctx);
    }
    printf("  [task A] done — return to main\n");
    switch_to(&task_a_ctx, &main_ctx);
    /* unreachable */
    abort();
}

static void task_b(void)
{
    for (int i = 1; i <= 3; i++) {
        printf("  [task B] slice %d\n", i);
        switch_to(&task_b_ctx, &task_a_ctx);
    }
    printf("  [task B] done — return to main\n");
    switch_to(&task_b_ctx, &main_ctx);
    abort();
}

static void bootstrap_task(struct context *ctx, uint8_t *stack, void (*entry)(void))
{
    /*
     * Fabricate a context as if the task had called switch_to and is about
     * to return into `entry`. On switch_to restore: ret jumps to entry.
     */
    uint64_t *top = (uint64_t *)(stack + STACK_SIZE);
    /* Keep 16-byte alignment required by AAPCS64. */
    top = (uint64_t *)(((uintptr_t)top) & ~0xFULL);

    ctx->x19 = 0;
    ctx->x20 = 0;
    ctx->x21 = 0;
    ctx->x22 = 0;
    ctx->x23 = 0;
    ctx->x24 = 0;
    ctx->x25 = 0;
    ctx->x26 = 0;
    ctx->x27 = 0;
    ctx->x28 = 0;
    ctx->x29 = 0;
    ctx->x30 = (uint64_t)entry;
    ctx->sp = (uint64_t)top;
}

int main(void)
{
    printf("=== AstraOS cooperative context-switch demo ===\n");
    bootstrap_task(&task_a_ctx, stack_a, task_a);
    bootstrap_task(&task_b_ctx, stack_b, task_b);

    printf("main: switching into task A\n");
    switch_to(&main_ctx, &task_a_ctx);
    printf("main: both tasks finished\n");
    return 0;
}
