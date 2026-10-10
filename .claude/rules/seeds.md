---
paths:
  - "seeds/**"
  - "tools/seal_confirmatory_seed.py"
  - "lpcstudy/config.py"
  - "lpcstudy/__main__.py"
---

# Seed rules (LPC.PC.7, NVVUQ.18)

- **Development seeds only.** Development runs use only the `DEV-n` seeds in `seeds/development_seeds.json`. New seeds are appended there with who drew them and how.
- **IMPORTANT: never touch the confirmatory seed.** Agents never draw, request, read, guess or run the confirmatory seed. Never run `tools/seal_confirmatory_seed.py`, and never use the `--confirmatory` path, without the owner's per-action authorization (LPC.AUTH.6).
- **Code that handles seeds** refuses unknown seed ids, raw integer seeds and mismatched commitments. Any change to it needs owner review before the freeze (LPC.PC.11).
