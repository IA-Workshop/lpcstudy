#!/usr/bin/env python3
"""V1 of WU-0005.4: compare the smoke results.json before (221ae9a) and after the change, leaf by leaf.

Usage: python3 -I docs/agent/notes/2026-10-11-wu0005-4-v1-compare.py BEFORE.json AFTER.json

A leaf is addressed by the tuple of keys (list items by index). Floats compare by IEEE bytes
(struct.pack('<d')), so 0.0 and -0.0 differ and NaN equals NaN with the same bits; ints, bools,
strings and None compare by type and value. Excluded: ``provenance`` and every leaf whose last key
contains ``seconds`` (wall-clock). Verdict (exit code 0 only if all hold):

* every leaf of BEFORE is in AFTER and identical, except the schema leaves
  (``handling/schema`` and ``systems/*/handling/schema``: ``lpcstudy.handling/1`` -> ``/2``);
* every leaf only in AFTER lies inside a ``handling`` block (``handling/...`` or
  ``systems/*/handling/...``, including the robustness handling) and either under an ``lm`` key
  (the new ``lm`` blocks) or has the last key ``lm_nonfinite_cost`` or ``lm_nonfinite_jacobian``
  (the two new counters: cells, by_kind, totals, run totals). A new ``lm_nonfinite_*`` leaf outside
  ``handling`` is not allowed.

Anything else is printed and is a defect: halt and /refer (WU-0005.4 V1).
"""
import json
import struct
import sys

SCHEMA_OLD, SCHEMA_NEW = "lpcstudy.handling/1", "lpcstudy.handling/2"


def leaves(node, path=()):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from leaves(value, (*path, str(key)))
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from leaves(value, (*path, f"[{i}]"))
    else:
        yield path, node


def keep(path):
    return path[0] != "provenance" and "seconds" not in path[-1]


def same(a, b):
    if isinstance(a, float) and isinstance(b, float):
        return struct.pack("<d", a) == struct.pack("<d", b)
    return type(a) is type(b) and a == b


def is_new_ok(path):
    in_handling = "handling" in path
    return in_handling and ("lm" in path or path[-1] in ("lm_nonfinite_cost", "lm_nonfinite_jacobian"))


def main(before_path, after_path):
    before = {p: v for p, v in leaves(json.load(open(before_path))) if keep(p)}
    after = {p: v for p, v in leaves(json.load(open(after_path))) if keep(p)}
    changed, removed, new_bad, schema = [], [], [], 0
    for path, value in before.items():
        if path not in after:
            removed.append(path)
        elif not same(value, after[path]):
            if (path[-1] == "schema" and "handling" in path and value == SCHEMA_OLD
                    and after[path] == SCHEMA_NEW):
                schema += 1
            else:
                changed.append(path)
    added = [p for p in after if p not in before]
    new_bad = [p for p in added if not is_new_ok(p)]
    print(f"leaves before {len(before)}, after {len(after)}; identical {len(before) - len(changed) - len(removed) - schema}; "
          f"schema {schema}; changed {len(changed)}; removed {len(removed)}; new {len(added)} "
          f"(allowed {len(added) - len(new_bad)}, not allowed {len(new_bad)})")
    for title, paths in (("CHANGED", changed), ("REMOVED", removed), ("NEW, NOT ALLOWED", new_bad)):
        for p in paths[:20]:
            print(f"  {title}: {'/'.join(p)}")
    return 0 if not (changed or removed or new_bad) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
