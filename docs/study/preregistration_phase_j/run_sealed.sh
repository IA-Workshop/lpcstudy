#!/usr/bin/env bash
# Phase J confirmatory runs, CONF-5 to CONF-9 (pre-registration section 5). Human owner only.
#
# Run from the root of a clean worktree checked out at tag freeze-j:
#   bash docs/study/preregistration_phase_j/run_sealed.sh
#
# 1. Asks for the seed and salt of CONF-5 to CONF-9 (hidden input) and checks each pair
#    against its ledger commitment before anything runs. Nothing is written to disk.
# 2. Detaches (setsid nohup), takes the GPU lock once and holds it for the whole session,
#    then runs the five official runs and the five regeneration runs, one at a time:
#      runs/confirmatory/phasej-CONF-n        official
#      runs/confirmatory/phasej-CONF-n-regen  regeneration
#    Each run's cache starts from the pinned lyapunov.json. The command is the one in
#    section 5; the lock is held by this script instead of a flock per run.
# 3. A refused or crashed run is logged and not repeated; the next run starts.
#
# Progress: runs/confirmatory/phasej-runs.log (one line per run start and end).
# Exit 75 when the GPU lock is held or a preset run is active; 64 on a bad input or tree.
set -uo pipefail

ids=(CONF-5 CONF-6 CONF-7 CONF-8 CONF-9)
py="${LPC_PYTHON:-/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python}"
lock=/tmp/lpcstudy-gpu.lock
pinned=docs/study/preregistration_phase_j/lyapunov.json
pinned_sha=852ce1f67cdcc55275f388c72817348b1b83e2146b4751c8c8aedc7a85453417
log=runs/confirmatory/phasej-runs.log

say() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*"; }
refuse() { echo "run_sealed: $*" >&2; exit "${2:-64}"; }

if [ "${_LPC_PHJ_STAGE:-}" != run ]; then
    # ---- Foreground: checks and seed entry ----
    [ -f "$pinned" ] && [ -d lpcstudy ] || refuse "run from the root of the freeze-j worktree"
    [ "$(git describe --exact-match --tags HEAD 2>/dev/null)" = freeze-j ] \
        || refuse "HEAD is not tag freeze-j"
    [ -z "$(git status --porcelain --untracked-files=no)" ] || refuse "the working tree is not clean"
    [ "$(sha256sum "$pinned" | cut -d' ' -f1)" = "$pinned_sha" ] || refuse "pinned lyapunov.json hash differs"
    "$py" -c 'import lpcstudy' 2>/dev/null || refuse "cannot import lpcstudy with $py (set LPC_PYTHON)"
    for id in "${ids[@]}"; do
        for suffix in "" -regen; do
            [ ! -e "runs/confirmatory/phasej-$id$suffix" ] \
                || refuse "runs/confirmatory/phasej-$id$suffix exists; never overwritten"
        done
    done
    pgrep -f "lpcstudy --preset" >/dev/null && refuse "a preset run is active" 75
    flock -n "$lock" true || refuse "the GPU lock is held" 75

    for id in "${ids[@]}"; do
        var="${id/-/}"
        read -rsp "$id seed: " seed; echo
        read -rsp "$id salt: " salt; echo
        if ! LPC_CONF_SEED="$seed" LPC_CONF_SALT="$salt" "$py" -c '
import os, sys
from lpcstudy.seeds import LEDGER_PATH, SeedRefusal, confirmatory_seed
try:
    confirmatory_seed(os.environ, LEDGER_PATH, sys.argv[1])
except SeedRefusal as exc:
    sys.exit(f"{sys.argv[1]}: {exc}")
' "$id"; then
            refuse "$id: seed or salt rejected; nothing was started"
        fi
        export "${var}_SEED=$seed" "${var}_SALT=$salt"
        echo "$id: matches its ledger commitment"
    done
    unset seed salt

    mkdir -p runs/confirmatory
    export _LPC_PHJ_STAGE=run
    setsid nohup bash "$0" >>"$log" 2>&1 </dev/null &
    echo "Started in the background (pid $!). Ten runs of about 30 min each, about 5.5 h."
    echo "Progress: tail -n 20 $log"
    exit 0
fi

# ---- Background: the runs ----
exec 9>>"$lock"
flock -n 9 || { say "GPU lock held; nothing run"; exit 75; }
threads=4
export LPC_THREADS=$threads OMP_NUM_THREADS=$threads MKL_NUM_THREADS=$threads \
    OPENBLAS_NUM_THREADS=$threads PJRT_NPROC=$threads NPROC=$threads
say "session start: commit $(git rev-parse HEAD), python $py, GPU lock held"

failed=0
for suffix in "" -regen; do
    for id in "${ids[@]}"; do
        var="${id/-/}"
        seed_var="${var}_SEED" salt_var="${var}_SALT"
        out="runs/confirmatory/phasej-$id$suffix"
        mkdir -p "$out/phasej/cache"
        cp "$pinned" "$out/phasej/cache/lyapunov.json"
        say "start $id${suffix:- official} -> $out"
        start=$(date +%s)
        LPC_CONF_SEED="${!seed_var}" LPC_CONF_SALT="${!salt_var}" \
            env JAX_PLATFORMS=cuda XLA_PYTHON_CLIENT_PREALLOCATE=false \
            "$py" -m lpcstudy --preset phasej --confirmatory --seed-id "$id" \
            --skip-robustness --states-dump --out "$out" >"$out/console.log" 2>&1
        rc=$?
        [ "$rc" -eq 0 ] || failed=$((failed + 1))
        say "end   $id${suffix:- official} exit=$rc seconds=$(( $(date +%s) - start ))" \
            "cache_sha256=$(sha256sum "$out/phasej/cache/lyapunov.json" | cut -d' ' -f1)"
    done
done
for id in "${ids[@]}"; do unset "${id/-/}_SEED" "${id/-/}_SALT"; done
say "session end: 10 runs, $failed with a nonzero exit"
