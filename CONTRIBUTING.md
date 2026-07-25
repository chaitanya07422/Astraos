# Contributing to AstraOS

Thanks for wanting to improve the guide. AstraOS is an educational project —
correctness and clarity for learners matter more than cleverness.

## Before you start

1. Read [`docs/PRD.md`](docs/PRD.md) — it is the source of truth for scope.
2. Check [`ROADMAP.md`](ROADMAP.md) so you do not invent work outside the
   current phase goals.
3. Open an issue first for anything larger than a typo or obvious bugfix.

## How to contribute

- **Docs / lessons:** follow the Documentation Standard in the PRD (all 14
  sections). Define acronyms on first use. Commands must be copy-paste runnable
  with expected output. Troubleshooting sections need real error messages.
- **Code / experiments:** keep changes inside the existing top-level layout
  (`experiments/`, `drivers/`, etc.). Do not add new top-level folders without
  updating the PRD.
- **Commits:** use the PRD prefixes (`docs:`, `lesson:`, `driver:`, `kernel:`,
  `boot:`, `rootfs:`, `experiment:`, `refactor:`, `fix:`).

## Pull requests

- One logical change per PR.
- Say what you tested (commands + observed output).
- If you intentionally deviate from the PRD, say so in the PR so the PRD can be
  updated.

## License

By contributing, you agree that code is MIT-licensed and written documentation
under `docs/` is CC BY-SA 4.0, as described in [`LICENSE`](LICENSE).
