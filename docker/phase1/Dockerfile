# AstraOS Phase 1 — AArch64 Linux build/run environment
# linux/arm64 matches the RK3566 target ABI (Apple Silicon runs natively;
# other hosts use Docker's emulation).
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        binutils \
        gdb \
        make \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work

# Default: interactive shell for make/gdb
CMD ["bash"]
