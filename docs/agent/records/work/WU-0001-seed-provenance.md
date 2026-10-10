# WU-0001: Seed registry, confirmatory-seed guard, run provenance

| Field | Value |
| --- | --- |
| Status | planned |
| Class | CSQ3 development; the code becomes part of the CSQ2 pipeline at the freeze |
| Agent(s) | — |

## Plan

**Scope.**

- **Command-line seeds.** Add `--seed-id DEV-n` (reads `seeds/development_seeds.json`) and `--confirmatory` (reads the seed and salt from the environment variables `LPC_CONF_SEED` and `LPC_CONF_SALT`, never from a file in the repository) to `python -m lpcstudy`.
- **Commitment check.** Verify a confirmatory seed against the latest ledger `commitment` entry for `CONF-1`, using `tools/seal_confirmatory_seed.make_commitment`.
- **Refusals.** Refuse loudly (PRIME.4) on:
  - an unknown seed id;
  - a missing or mismatched commitment;
  - `--confirmatory` without the environment variables;
  - a raw integer seed passed on the command line.
- **Provenance.** Write the block LPC.PC.18 requires into `results.json` and the `RESULTS.md` header:
  - the seed id, never the confirmatory value;
  - the code commit and the dirty flag;
  - the preset and full configuration;
  - Python and package versions;
  - the device, and whether JAX x64 is enabled;
  - wall-clock time and peak memory (LPC.PC.22).
- **Labels.** Header label `DEVELOPMENT (DEV-n): not a hypothesis test` or `CONFIRMATORY: UNPROMOTED`.
- **Out of scope:** any change to the scientific computation.

**Definition of done.** All refusals are tested; provenance appears in smoke output; the existing tests still pass; reviewed.

**Acceptance criteria.**

- **Unit tests** for each refusal path, and for the commitment check with a known seed and salt: the expected digest is computed independently in the test with `hashlib`.
- **Smoke regression.** `--seed-id DEV-0` smoke output matches the v1 smoke output's numbers bit for bit on CPU, since DEV-0 equals the v1 default seed. The provenance block is present and parses.
- **Workspace check.** Running with `--confirmatory` in the test environment uses a throwaway ledger fixture, never the real ledger or a real seed.

**Affected checks.** `tests/`; the smoke preset.

**Owner checkpoint.** The owner reviews the seed and provenance code before the freeze (LPC.PC.11).

## Log

## Review

## Audit
