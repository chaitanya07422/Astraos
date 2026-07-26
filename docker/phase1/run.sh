#!/usr/bin/env bash
# Run a command inside the Phase 1 AArch64 Linux container.
# Usage (from repo root):
#   ./docker/phase1/run.sh make -C experiments/phase1-asm run
#   ./docker/phase1/run.sh bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
IMAGE="astraos-phase1:bookworm"

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "Building $IMAGE (first time only)..."
  docker build --platform linux/arm64 -t "$IMAGE" "$ROOT/docker/phase1"
fi

if [[ $# -eq 0 ]]; then
  set -- bash
fi

TTY_FLAGS=(-i)
if [[ -t 0 && -t 1 ]]; then
  TTY_FLAGS=(-it)
fi

exec docker run --rm "${TTY_FLAGS[@]}" \
  --platform linux/arm64 \
  -v "$ROOT:/work" \
  -w /work \
  "$IMAGE" \
  "$@"
