#!/usr/bin/env bash
# Phase J confirmatory analysis, CONF-5 to CONF-9 (pre-registration section 7 and the
# regeneration comparison of section 5). Human owner only (P-6, ledger seq 56).
# POST-FREEZE helper: written after tag freeze-j; it runs the frozen tools unchanged.
#
# Run from the root of the clean freeze-j worktree that holds the sealed runs:
#   bash /path/to/run_sealed_analysis.sh
#
# 1. Asks for the five lines "CONF-n <seed> <salt>" (one paste, hidden input) and checks
#    each pair against its ledger commitment. Nothing is written to disk.
# 2. Detaches (setsid nohup) and, on the CPU, for the five official runs and then the five
#    regeneration runs: tools/lpc_contrib.py --sealed, then tools/lpc_contrib_ce.py
#    --sealed --abd, into <run>/contrib-j. Then tools/lpc_confirm.py once on the official
#    analyses (phasej-confirm) and once on the regeneration analyses
#    (phasej-confirm-regen).
#    Both analysis tools refuse any argument that contains the word "confirmatory"
#    (DEF-0034), so every path is given relative to runs/confirmatory, which is the
#    working directory of the tools. The tools find the repository from their own
#    location, so nothing else changes.
# 3. If any analysis step fails, lpc_confirm is not run; the failure is reported.
#
# Progress: runs/confirmatory/phasej-analysis.log. About 30 min per run, about 5 h.
set -uo pipefail

ids=(CONF-5 CONF-6 CONF-7 CONF-8 CONF-9)
py="${LPC_PYTHON:-/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python}"
base=runs/confirmatory
log="$base/phasej-analysis.log"
self="$(realpath "$0")"

say() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*"; }
refuse() { echo "run_sealed_analysis: $*" >&2; exit "${2:-64}"; }

if [ "${_LPC_PHJ_STAGE:-}" != analysis ]; then
    # ---- Foreground: checks and seed entry ----
    [ -d lpcstudy ] && [ -d "$base" ] || refuse "run from the root of the freeze-j worktree"
    [ "$(git describe --exact-match --tags HEAD 2>/dev/null)" = freeze-j ] \
        || refuse "HEAD is not tag freeze-j"
    [ -z "$(git status --porcelain -- lpcstudy tools)" ] || refuse "lpcstudy/ or tools/ is not clean"
    "$py" -c 'import lpcstudy' 2>/dev/null || refuse "cannot import lpcstudy with $py (set LPC_PYTHON)"
    for id in "${ids[@]}"; do
        for suffix in "" -regen; do
            r="$base/phasej-$id$suffix"
            [ -f "$r/phasej/results.json" ] || refuse "$r/phasej/results.json is missing"
            [ ! -e "$r/contrib-j" ] || refuse "$r/contrib-j exists; never overwritten"
        done
    done
    for o in phasej-confirm phasej-confirm-regen; do
        [ ! -e "$base/$o" ] || refuse "$base/$o exists; never overwritten"
    done
    pgrep -f "lpcstudy --preset|lpc_contrib" >/dev/null && refuse "a run or an analysis is active" 75

    echo "Paste the five lines 'CONF-n <seed> <salt>' (input hidden; press Enter after the last line):"
    declare -A seen=()
    while [ "${#seen[@]}" -lt "${#ids[@]}" ]; do
        IFS= read -rs line || [ -n "$line" ] \
            || refuse "input ended after ${#seen[@]} of ${#ids[@]} lines; nothing was started"
        read -r id seed salt extra <<<"$line"
        [ -n "${id:-}" ] || continue
        [[ " ${ids[*]} " == *" $id "* ]] || refuse "a line does not start with one of ${ids[*]}; nothing was started"
        [ -z "${seen[$id]:-}" ] || refuse "$id was given twice; nothing was started"
        [ -n "${salt:-}" ] && [ -z "${extra:-}" ] || refuse "$id: expected '$id <seed> <salt>'; nothing was started"
        var="${id/-/}"
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
        seen[$id]=1
        echo "$id: matches its ledger commitment"
    done
    unset line seed salt

    export _LPC_PHJ_STAGE=analysis
    setsid nohup bash "$self" >>"$log" 2>&1 </dev/null &
    echo "Started in the background (pid $!). Ten analyses of about 30 min each, about 5 h."
    echo "Progress: tail -n 20 $log"
    exit 0
fi

# ---- Background: the analysis, from runs/confirmatory ----
export JAX_PLATFORMS=cpu XLA_PYTHON_CLIENT_PREALLOCATE=false LPC_THREADS=4 \
    OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
say "session start: commit $(git rev-parse HEAD), python $py"
cd "$base" || { say "cannot enter $base"; exit 1; }
tools=../../tools
docs=../../docs/study/preregistration_phase_j

failed=0
for suffix in "" -regen; do
    for id in "${ids[@]}"; do
        var="${id/-/}"
        seed_var="${var}_SEED" salt_var="${var}_SALT"
        r="phasej-$id$suffix"
        o="$r/contrib-j"
        say "start $r"
        start=$(date +%s)
        LPC_CONF_SEED="${!seed_var}" LPC_CONF_SALT="${!salt_var}" nice -n 19 \
            "$py" "$tools/lpc_contrib.py" "$r/phasej" --sealed --jobs 4 --out "$o" \
            >"$r/contrib-j.abd.log" 2>&1
        abd=$?
        ce=skipped
        if [ "$abd" -eq 0 ]; then
            LPC_CONF_SEED="${!seed_var}" LPC_CONF_SALT="${!salt_var}" nice -n 19 \
                "$py" "$tools/lpc_contrib_ce.py" "$r/phasej" --sealed --jobs 4 \
                --abd "$o/contrib.json" --out "$o" >"$r/contrib-j.ce.log" 2>&1
            ce=$?
        fi
        [ "$abd" -eq 0 ] && [ "$ce" = 0 ] || failed=$((failed + 1))
        say "end   $r abd=$abd ce=$ce seconds=$(( $(date +%s) - start ))"
    done
done
for id in "${ids[@]}"; do unset "${id/-/}_SEED" "${id/-/}_SALT"; done

if [ "$failed" -ne 0 ]; then
    say "session end: $failed of 10 analyses failed; lpc_confirm not run"
    exit 1
fi
for suffix in "" -regen; do
    dirs=()
    for id in "${ids[@]}"; do dirs+=("phasej-$id$suffix/contrib-j"); done
    out="phasej-confirm$suffix"
    "$py" "$tools/lpc_confirm.py" --claims "$docs/claims.json" --pinned "$docs/lyapunov.json" \
        "${dirs[@]}" --out "$out" >"$out.log" 2>&1
    say "lpc_confirm $out exit=$? $(tail -n 1 "$out.log")"
done
say "session end: 10 analyses, lpc_confirm twice"
