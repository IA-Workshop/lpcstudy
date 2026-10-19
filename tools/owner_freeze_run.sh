#!/usr/bin/env bash
# Owner-run driver for the freeze and the launch preparation (WU-0004.2-.8, WU-0015.1).
# Written by an agent for the owner to RUN; no agent runs it (the sealed seed and the freeze are the owner's acts).
#
# Usage:  tools/owner_freeze_run.sh <step>
#   preflight   read-only checks; prints what blocks the freeze (run first, run often)
#   tests       the freeze gate: unit, integration, slow, gpu (LPC_GATE=freeze); appends summary lines to a GATE record
#   merge       merge develop into main with a merge commit (needs a clean main checkout)
#   lock        write requirements.lock from the installed packages and commit it
#   ledger      append a `ruling` entry (DEC-0028 to DEC-0033) and the freeze `classification` entry (asks for your name; you enter the other entries yourself)
#   tag         commit pending ledger changes, hash the v3 export, create the annotated tag freeze-1
#   prerun      the WU-0015.1 checks on the tagged tree; prints the launch conditions
#
# Between `ledger` and `tag` YOU run the seed-sealing step of WU-0004.6 (draw CONF-1, store seed and salt outside the
# repository, append the commitment entry). That step, and the launch of the sealed run (WU-0015.2), are NOT in this
# script on purpose: they are owner-only (LPC.PC.7, LPC.AUTH.6) and a hook blocks agents from the commands.
#
# Environment: REPO (default: the checkout this script is in), V3_EXPORT (path of the v3 export, needed by `tag`).
# In plain words: this script is the owner's checklist for the freeze, the point after which
# the study code and design may no longer change and the sealed confirmatory run can be
# prepared. Each step above is a shell function below. It checks the state of the repository,
# runs the tests, merges, records the exact package versions, writes the governance ledger
# entry and creates the tag freeze-1. The usage text that the script prints for a missing or
# unknown step is lines 2 to 18 of this file, so those lines must stay as they are.
set -euo pipefail

REPO="${REPO:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$REPO"
PY="${LPC_PYTHON:-$REPO/.venv/bin/python}"
[ -x "$PY" ] || PY=python3
TODAY="$(date +%F)"
GATE_FILE="docs/agent/records/work/GATE-${TODAY}-freeze.md"
fail=0
say() { printf '%s\n' "$*"; }
bad() { say "BLOCKED: $*"; fail=1; }
ok() { say "ok:      $*"; }

preflight() {
  say "== preflight in $REPO =="
  local branch; branch="$(git rev-parse --abbrev-ref HEAD)"
  say "branch $branch, commit $(git rev-parse --short HEAD)"
  [ -z "$(git status --porcelain)" ] && ok "working tree clean" \
    || { bad "working tree not clean (a sealed run is refused on a dirty tree):"; git status --short | head -20; }
  local n
  n="$(git branch --no-merged develop --list 'wu/*' 2>/dev/null | wc -l)"
  [ "$n" = 0 ] && ok "every wu/* branch is merged into develop" \
    || { say "warning: $n wu/* branches are not merged into develop:"; git branch --no-merged develop --list 'wu/*' | head -20; }
  "$PY" tools/ledger.py verify >/dev/null 2>&1 && ok "ledger chain verifies" || bad "ledger verify failed"
  "$PY" - <<'EOF' || fail=1
import importlib.metadata as m, re, sys
pins = {}
for line in open("requirements.txt"):
    line = line.strip()
    if line and not line.startswith("#") and "==" in line:
        name, ver = line.split("==", 1)
        pins[re.sub(r"\[.*\]", "", name).lower().replace("_", "-")] = ver
bad = [(n, v, m.version(n)) for n, v in pins.items() if m.version(n) != v]
print("ok:      installed versions match requirements.txt" if not bad else f"BLOCKED: version mismatch {bad}")
sys.exit(1 if bad else 0)
EOF
  if git rev-parse -q --verify refs/tags/freeze-1 >/dev/null; then say "note:    tag freeze-1 exists at $(git rev-parse --short freeze-1)"; fi
  if ps -eo args | grep -E "^[^ ]*python[0-9.]* .*-m (lpcstudy|pytest)" | grep -v grep >/dev/null; then bad "a run or a test is active"; else ok "no active run or test"; fi
  [ "$fail" = 0 ] && say "preflight: nothing blocks" || say "preflight: FIX THE ITEMS ABOVE"
  return "$fail"
}

tests() {
  say "== freeze gate (LPC_GATE=freeze); summary lines go to $GATE_FILE =="
  [ -z "$(git status --porcelain)" ] || { say "tree not clean: commit first"; exit 2; }
  { printf '\n# Freeze gate %s, commit %s (owner script)\n' "$TODAY" "$(git rev-parse HEAD)"; } >> "$GATE_FILE"
  local rc=0 tier path out
  for spec in "unit tests/unit" "integration tests/integration" "slow tests/slow" "gpu tests/gpu"; do
    set -- $spec; tier="$1"; path="$2"
    say "-- $tier"
    set +e; out="$(LPC_GATE=freeze tools/run_tests.sh "$tier" "$path" 2>&1)"; local r=$?; set -e
    printf '%s\n' "$out" | tail -n 6
    { printf -- '- `LPC_GATE=freeze tools/run_tests.sh %s %s`: exit %s, %s\n' "$tier" "$path" "$r" "$(printf '%s\n' "$out" | tail -n 2 | tr '\n' ' ')"; } >> "$GATE_FILE"
    [ "$r" = 0 ] || rc=1
  done
  say "gate record appended to $GATE_FILE (commit it). Slow tier timeout is 3600 s; if it times out that is a finding, not a pass."
  return "$rc"
}

merge() {
  local branch; branch="$(git rev-parse --abbrev-ref HEAD)"
  [ "$branch" = main ] || { say "run this in the main checkout, on main (now on $branch)"; exit 2; }
  if [ -n "$(git status --porcelain)" ]; then
    say "BLOCKED: main is dirty. A sealed run is refused on a dirty tree, so these must be committed (or discarded) by you first:"
    git status --short
    exit 2
  fi
  git merge --no-ff develop -m "Merge develop into main: freeze candidate (owner-authorized 2026-10-18)"
  say "merged; main is at $(git rev-parse --short HEAD)"
}

lock() {
  [ -z "$(git status --porcelain)" ] || { say "tree not clean: commit first"; exit 2; }
  "$PY" - <<'EOF'
import importlib.metadata as m
rows = sorted((d.metadata["Name"], d.version) for d in m.distributions())
open("requirements.lock", "w").write("".join(f"{n}=={v}\n" for n, v in rows))
print(f"requirements.lock: {len(rows)} packages")
EOF
  git add requirements.lock
  git commit -m "Freeze: requirements.lock from the installed packages (owner-run, WU-0004.7)"
}

ledger() {
  say "Two entries: a ruling entry for DEC-0028 to DEC-0033, then the freeze classification (entry to CSQ2, LPC.PC.5)."
  say "Enter the other drafted entries yourself, as you choose:"
  say "  docs/agent/notes/2026-10-18-ledger-batch-draft.md"
  read -r -p "Your name for the actor field: " actor
  [ -n "$actor" ] || { say "actor required"; exit 2; }
  local v3="docs/study/proposal_and_methods_v3.md" v3sum head branch
  [ -f "$v3" ] || { say "no such file: $v3"; exit 2; }
  v3sum="$(sha256sum "$v3" | cut -d' ' -f1)"
  head="$(git rev-parse HEAD)"
  branch="$(git rev-parse --abbrev-ref HEAD)"
  "$PY" tools/ledger.py append --type ruling --actor "$actor" --role "human owner" \
    --authority "PRIME.1; DEC-0028 to DEC-0033" \
    --summary "Owner rulings of 2026-10-11 to 2026-10-18 as recorded in decisions.md DEC-0028 to DEC-0033: reproducibility tolerance, confirmatory sample size, rehearsal and comparison-tool rulings, CPU as the official device, freeze-blocker rulings B5 to B11, freeze-audit rulings M1 to M4" \
    --data "{\"decisions\": [\"DEC-0028\", \"DEC-0029\", \"DEC-0030\", \"DEC-0031\", \"DEC-0032\", \"DEC-0033\"], \"source\": \"docs/agent/notes/2026-10-11-amendments-for-owner.md; docs/agent/records/audits/2026-10-18-freeze.md\", \"audit_rulings_quote\": \"M1 amend / M2 extrapolate / M3 report only / M4 apply this\"}"
  "$PY" tools/ledger.py append --type classification --actor "$actor" --role "human owner" \
    --authority "LPC.PC.5, LPC.PC.8; owner decision of 2026-10-18; freeze-audit rulings M2, M3, M4" \
    --summary "Freeze: entry to CSQ2 at commit $head. Governing design text: $v3 at SHA-256 $v3sum (the Claude Doc is a working copy). Bitwise agreement of the CPU run at the full preset and LPC_THREADS=8 is extrapolated from smoke and GPU pilot size. The gain-bound screen (ROADMAP WU-0002.15) is a post-freeze change to a reported-only quantity." \
    --data "{\"commit\": \"$head\", \"branch\": \"$branch\", \"v3_governing_file\": \"$v3\", \"v3_sha256\": \"$v3sum\", \"claude_doc_status\": \"working copy, not the governing text\", \"bitwise_declaration\": \"measured at smoke size (CPU, 4 and 8 threads) and GPU pilot size; extrapolated to the full preset at LPC_THREADS=8; a regeneration that is not bitwise is judged by the per-quantity tolerances (v3 section 9 item 4)\", \"post_freeze_reported_only\": \"ROADMAP WU-0002.15 gain-bound screen (DEC-0033, M3)\"}"
  "$PY" tools/ledger.py verify
  say "Now YOU run the seed-sealing step of WU-0004.6 (draw CONF-1, store seed and salt outside the repository, commitment entry). Then run: tools/owner_freeze_run.sh tag"
}

tag() {
  : "${V3_EXPORT:?set V3_EXPORT to the path of the v3 export}"
  [ -f "$V3_EXPORT" ] || { say "no such file: $V3_EXPORT"; exit 2; }
  if [ -n "$(git status --porcelain)" ]; then
    say "pending changes (expected: the ledger only):"; git status --short
    local other; other="$(git status --porcelain | grep -v 'governance/ledger' || true)"
    [ -z "$other" ] || { say "BLOCKED: changes other than the ledger; commit them yourself first"; exit 2; }
    git add -u docs/agent/governance
    git commit -m "Freeze: ledger entries (classification, commitment)"
  fi
  local sum; sum="$(sha256sum "$V3_EXPORT" | cut -d' ' -f1)"
  git tag -a freeze-1 -m "Freeze 1: commit $(git rev-parse HEAD); v3 export sha256 $sum; requirements.lock committed"
  say "tagged freeze-1 at $(git rev-parse --short HEAD); v3 export sha256 $sum"
  say "Record that hash in the ledger as a note (tools/ledger.py append --type note ...)."
}

prerun() {
  say "== WU-0015.1 pre-run checks =="
  [ "$(git describe --tags --exact-match 2>/dev/null)" = freeze-1 ] && ok "HEAD is exactly freeze-1" || bad "HEAD is not exactly freeze-1"
  [ -z "$(git status --porcelain)" ] && ok "working tree clean" || bad "working tree not clean"
  [ -z "$(git status --porcelain --ignored | grep -v -E '^!! (\.venv|__pycache__|.*\.pyc|\.pytest_cache|runs/)' )" ] \
    && ok "no unexpected ignored or untracked paths" || { bad "unexpected ignored/untracked paths:"; git status --porcelain --ignored | head; }
  [ "$(grep -v -E '^\s*(#|$)' .git/info/exclude 2>/dev/null | tr -d ' \n')" = ".venv" ] && ok ".git/info/exclude holds only .venv" || bad ".git/info/exclude holds more than .venv"
  [ ! -e .git/info/attributes ] && ok "no .git/info/attributes" || bad ".git/info/attributes exists"
  [ -z "$(git config --show-origin --get-regexp '^(filter\.|core\.attributesfile|core\.fsmonitor)' 2>/dev/null)" ] \
    && ok "no git filter, attributes file or fsmonitor configured" || bad "git filter/attributes/fsmonitor configured"
  "$PY" - <<'EOF' || fail=1
import importlib.metadata as m, sys
want = {}
for line in open("requirements.lock"):
    if "==" in line:
        n, v = line.strip().split("==", 1); want[n] = v
bad = [(n, v, m.version(n)) for n, v in want.items() if n in {d.metadata["Name"] for d in m.distributions()} and m.version(n) != v]
missing = [n for n in want if n not in {d.metadata["Name"] for d in m.distributions()}]
print("ok:      environment matches requirements.lock" if not (bad or missing) else f"BLOCKED: lock mismatch {bad} missing {missing}")
sys.exit(1 if (bad or missing) else 0)
EOF
  ps -eo args | grep -E "^[^ ]*python[0-9.]* .*-m (lpcstudy|pytest)" | grep -v grep >/dev/null && bad "a run or test is active" || ok "no active run or test"
  "$PY" tools/ledger.py verify >/dev/null 2>&1 && ok "ledger verifies" || bad "ledger verify failed"
  if [ "$fail" = 0 ]; then
    say ""
    say "All checks pass. Launch conditions (owner ruling B4): the OFFICIAL run is on the CPU with LPC_THREADS=8 (about 4.7 h);"
    say "supply the seed and salt in your own shell environment at run time, as WU-0015.2 states; output outside the repository"
    say "or in an ignored path; the wrapper refuses a dirty tree. A GPU run of the same sealed seed is only a cross-check and"
    say "needs its own authorization. Record the per-action authorization entry (LPC.AUTH.6) before you launch."
  else
    say "pre-run: NOT READY"
  fi
  return "$fail"
}

case "${1:-}" in
  preflight) preflight ;;
  tests) tests ;;
  merge) merge ;;
  lock) lock ;;
  ledger) ledger ;;
  tag) tag ;;
  prerun) prerun ;;
  *) sed -n 2,18p "$0"; exit 64 ;;
esac
