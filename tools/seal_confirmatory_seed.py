"""Draw the confirmatory master seed and print its commitment (human owner only).

Run once, at the freeze, by the human owner. The seed and salt are printed once
and are not written to disk; store them outside the repository. Record only the
commitment in the ledger (see seeds/README.md).

The commitment is SHA-256 of the ASCII string "<seed>:<salt_hex>".
"""
from __future__ import annotations

import hashlib
import secrets


def make_commitment(seed: int, salt_hex: str) -> str:
    """Return the SHA-256 commitment of a seed and salt.

    Parameters
    ----------
    seed : int
        Master seed.
    salt_hex : str
        Salt as a hexadecimal string.

    Returns
    -------
    str
        Hexadecimal SHA-256 digest of ``f"{seed}:{salt_hex}"``.
    """
    return hashlib.sha256(f"{seed}:{salt_hex}".encode("ascii")).hexdigest()


def main() -> None:
    """Draw a 62-bit seed and a 128-bit salt and print them with the commitment."""
    seed = secrets.randbits(62)
    salt_hex = secrets.token_hex(16)
    print("CONF-1 seed :", seed)
    print("CONF-1 salt :", salt_hex)
    print("commitment  :", make_commitment(seed, salt_hex))
    print("Store seed and salt outside the repository. Record only the commitment.")


if __name__ == "__main__":
    main()
