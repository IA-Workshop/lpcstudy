# Seeds

Every run of `lpcstudy` is driven by one integer **master seed**. `lpcstudy.data.make_rng(seed, *labels)` derives an independent stream for each purpose from it: system, split, noise draws and network initialization. Changing the master seed changes every trajectory, library, noise draw and network.

There are two kinds of master seed. They are kept apart so that the confirmatory run tests the pre-registered design on data nobody has seen (project constitution LPC.PC.7).

| Kind | Where it lives | Who uses it | What its results are |
| --- | --- | --- | --- |
| Development (`DEV-n`) | `development_seeds.json` in this folder | anyone, any number of runs | development evidence only; never reported as hypothesis tests |
| Confirmatory (`CONF-1`) | outside the repository, held by the human owner until the confirmatory run; only its SHA-256 commitment is in the ledger | the human owner, or an agent under a per-action authorization | the pre-registered test, once promoted (QA.11) |

## Development seeds

- `DEV-0` (20261005) is the pilot seed, so its results have been seen. Use it to compare new code against the pilot.
- `DEV-1` to `DEV-4` are fresh, drawn on 2026-10-10 with `secrets.randbits(62)`.
- Add more by appending entries (never edit or remove one). Record who drew the seed and how.

## Confirmatory seed (owner only)

At the freeze, after the pre-registration snapshot is committed, the owner runs:

```
python tools/seal_confirmatory_seed.py
```

The script:

- draws a fresh 62-bit seed;
- prints it once;
- prints its SHA-256 commitment, salted with a 128-bit salt it also prints.

The owner then:

1. Stores the seed and salt outside the repository, for example in a password manager.
2. Appends the commitment to the ledger:

   ```
   python tools/ledger.py append --type commitment --actor "<owner>" --role "human owner" --summary "CONF-1 commitment" --data '{"seed_id":"CONF-1","sha256":"<hash>"}'
   ```

At the confirmatory run, the owner supplies the seed and salt. The code checks them against the ledger commitment and refuses to run on a mismatch (WU-0001). This proves the confirmatory seed was fixed before any confirmatory result existed.
