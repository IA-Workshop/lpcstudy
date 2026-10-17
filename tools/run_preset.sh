#!/usr/bin/env bash
# Run an lpcstudy preset on a registered DEVELOPMENT seed under the limits of LPC.AUTH.3.
#
# Usage: tools/run_preset.sh <preset> <seed-id> <out-dir> [--device cpu|gpu]
#                            [--systems S...] [--skip-robustness] [--estimator-refine-steps N]
#                            [--states-dump]
#
#   preset   smoke | pilot | full
#   seed-id  a DEV-n id listed in seeds/development_seeds.json (never a raw integer)
#   out-dir  must lie under <repo>/runs/, so that the weekly GPU tally sees every run
#
# Refusals (exit 64, one line on stderr, nothing started): any argument containing
# "confirmatory" (any case), a raw integer seed, an id not in the registry (or a registry with
# another schema), an unknown preset or argument, an out-dir outside runs/, an existing
# <out-dir>/<preset>/run.meta.json (it would erase GPU hours), or a seed the CLI cannot take.
# --estimator-refine-steps N (WU-0005.6, the iteration-doubling study) is passed to the CLI as it is:
# N is a canonical decimal integer from 1 to 999 (no sign, no leading zero), given once, else the
# wrapper refuses before the lock. The CLI itself refuses it with the confirmatory flag, which this
# wrapper never accepts. The meta file records it in "command".
# --states-dump (WU-0003.7b, WU-0003.11: the per-state dump of the rehearsal runs R1 and R5) is a
# bare flag, given once and passed to the CLI unchanged; with an argument (--states-dump X, or
# --states-dump=X) or given twice the wrapper refuses before the lock. The CLI itself refuses it with
# the confirmatory flag (which this wrapper never accepts) and with --report-only (which this wrapper
# never passes). The meta file records it in "command". Nothing else changes with it.
#
# Device: cpu for smoke, gpu for pilot and full (JAX_PLATFORMS cpu or cuda); thread variables
# are set from LPC_THREADS (1..99, default 4), as are PJRT_NPROC and NPROC (the XLA CPU thread
# pools); XLA_PYTHON_CLIENT_PREALLOCATE=false. XLA_FLAGS is never set or altered.
# Lock: pilot, full and any gpu run take `flock -n` on ${LPC_GPU_LOCK:-/tmp/lpcstudy-gpu.lock} at
# once (exit 75 if held, never wait). A smoke run on CPU takes no lock (4.5).
# Tally: pilot, full and any gpu run call `python3 -I tools/gpu_hours.py check --hours H` while
# holding the lock (H = 12 for gpu, 0 for cpu); exit 64 or 65 is propagated, any other failure
# or a missing tool gives 65 (fail closed).
# Seed: the CLI is probed with `--help`. If it has --seed-id the flag is passed. If not, only
# DEV-0 runs (the CLI default 20261005 is the registry's DEV-0), with a note; any other id is
# refused (needs --seed-id, WU-0001.1).
# Meta: <out-dir>/<preset>/run.meta.json (schema lpcstudy.run-meta/1) is written atomically at
# the start (end_utc, wall_seconds, exit_code null) and again at the end.
# Run: `timeout --kill-after=300 12h <python> -m lpcstudy --preset P --out OUT [...]`. Smoke runs
# in the foreground and returns the CLI's exit code. Pilot and full always start in the
# background (a subshell that ignores SIGHUP, console.log) and print "started pid=... console=... run_log=... meta=...".
# Exit codes: 64 refusal, 65 weekly GPU hours (or tally failure), 75 lock busy, else the CLI's.
# LPC_PYTHON selects the interpreter (else <root>/.venv/bin/python, else python3).

set -u

caller="$PWD"
self="$(realpath "${BASH_SOURCE[0]}")"
root="$(cd "$(dirname "$self")/.." && pwd -P)"
lock="$(realpath -m -- "${LPC_GPU_LOCK:-/tmp/lpcstudy-gpu.lock}")"

refuse() {
    echo "run_preset.sh: refused: $1" >&2
    exit 64
}

# Python helper for run.meta.json: start | pid | end. Atomic (temporary file, then replace).
# shellcheck disable=SC2016
META_PY='
import datetime as dt, json, os, shlex, sys

FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def iso(epoch):
    return dt.datetime.fromtimestamp(int(epoch), dt.timezone.utc).strftime(FORMAT)


def epoch_of(text):
    return int(dt.datetime.strptime(text, FORMAT).replace(tzinfo=dt.timezone.utc).timestamp())


def save(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


mode, meta = sys.argv[1], sys.argv[2]
if mode == "start":
    preset, seed, device, epoch, seed_flag, threads, pid, *command = sys.argv[3:]
    if os.path.lexists(meta):
        sys.exit("run.meta.json exists")
    save(meta, {
        "schema": "lpcstudy.run-meta/1", "preset": preset, "seed_id": seed,
        "start_utc": iso(epoch), "end_utc": None, "device": device, "wall_seconds": None,
        "exit_code": None, "seed_flag": seed_flag or None, "lpc_threads": int(threads),
        "command": shlex.join(command), "pid": int(pid)})
else:
    with open(meta) as handle:
        data = json.load(handle)
    if data.get("schema") != "lpcstudy.run-meta/1" or data.get("end_utc") is not None:
        sys.exit("not an open lpcstudy.run-meta/1 file")
    if mode == "pid":
        data["pid"] = int(sys.argv[3])
    else:
        epoch, code = int(sys.argv[3]), int(sys.argv[4])
        data["end_utc"] = iso(epoch)
        data["wall_seconds"] = epoch - epoch_of(data["start_utc"])
        data["exit_code"] = code
    save(meta, data)
'

meta_call() {
    python3 -I -c "$META_PY" "$@"
}

# on_signal <code>: forward TERM to the run, wait for it, record 128+signal, leave.
on_signal() {
    kill -TERM "$child" 2>/dev/null
    wait "$child" 2>/dev/null
    meta_call end "$meta" "$(date -u +%s)" "$1" || echo "run_preset.sh: WARNING: could not record the end in $meta" >&2
    exit "$1"
}

# run_recorded <meta> <command>...: run the command as a child and record its end in the meta.
run_recorded() {
    meta="$1"
    shift
    meta_call pid "$meta" "$BASHPID" || echo "run_preset.sh: WARNING: could not record the pid in $meta" >&2
    "$@" &
    child=$!
    if [ "${ignore_hup:-0}" = 1 ]; then trap '' HUP; else trap 'on_signal 129' HUP; fi
    trap 'on_signal 130' INT
    trap 'on_signal 143' TERM
    wait "$child"
    local code=$?
    trap - HUP INT TERM
    meta_call end "$meta" "$(date -u +%s)" "$code" || echo "run_preset.sh: WARNING: could not record the end in $meta" >&2
    return "$code"
}

for arg in "$@"; do
    lower="${arg,,}"
    [[ "$lower" != *confirmatory* ]] || refuse "an argument names the confirmatory path, which is owner-only (LPC.PC.7)"
done

[ "$#" -ge 3 ] || refuse "usage: run_preset.sh <smoke|pilot|full> <DEV-n> <out-dir> [--device cpu|gpu] [--systems S...] [--skip-robustness] [--estimator-refine-steps N] [--states-dump]"
preset="$1"
seed="$2"
out_arg="$3"
shift 3

device=""
systems=()
passthrough=()
refine_given=0
dump_given=0
while [ "$#" -gt 0 ]; do
    case "$1" in
        --device)
            [ "$#" -ge 2 ] && [[ "$2" == cpu || "$2" == gpu ]] || refuse "--device needs cpu or gpu"
            device="$2"
            shift 2
            ;;
        --systems)
            shift
            systems=()
            while [ "$#" -gt 0 ] && [[ "$1" != -* ]]; do
                [[ "$1" =~ ^[A-Za-z0-9_]+$ ]] || refuse "bad system name ${1@Q}"
                systems+=("$1")
                shift
            done
            [ "${#systems[@]}" -ge 1 ] || refuse "--systems needs at least one system name"
            ;;
        --skip-robustness)
            passthrough+=("$1")
            shift
            ;;
        --estimator-refine-steps)
            [ "$refine_given" = 0 ] || refuse "--estimator-refine-steps is given twice"
            [ "$#" -ge 2 ] && [[ "$2" =~ ^[1-9][0-9]{0,2}$ ]] || refuse "--estimator-refine-steps needs an integer from 1 to 999"
            refine_given=1
            passthrough+=("$1" "$2")
            shift 2
            ;;
        --states-dump)
            [ "$dump_given" = 0 ] || refuse "--states-dump is given twice"
            dump_given=1
            shift
            # A bare flag: a following word that is not another option is an argument (refused).
            [ "$#" -eq 0 ] || [[ "$1" == --* ]] || refuse "--states-dump takes no argument"
            passthrough+=(--states-dump)
            ;;
        --states-dump=*) refuse "--states-dump takes no argument" ;;
        *) refuse "unexpected argument ${1@Q}" ;;
    esac
done

case "$preset" in
    smoke | pilot | full) ;;
    *) refuse "unknown preset ${preset@Q} (smoke, pilot or full)" ;;
esac

[[ ! "$seed" =~ ^[0-9]+$ ]] || refuse "raw integer seed; use a DEV-n id, LPC.PC.7"
[[ "$seed" =~ ^DEV-[0-9]+$ ]] || refuse "seed id ${seed@Q} is not a DEV-n id of seeds/development_seeds.json (LPC.PC.7)"
# shellcheck disable=SC2016
registry_message="$(python3 -I -c '
import json, sys
path, ident = sys.argv[1:3]
try:
    with open(path) as handle:
        data = json.load(handle)
except (OSError, ValueError) as error:
    sys.exit(f"seed registry unreadable ({type(error).__name__})")
if not isinstance(data, dict) or data.get("schema") != "lpcstudy.seed-registry/1":
    sys.exit("seed registry has not the schema lpcstudy.seed-registry/1")
ids = [s.get("id") for s in data.get("seeds", []) if isinstance(s, dict)]
if ident not in ids:
    sys.exit(f"seed id {ident!r} is not in seeds/development_seeds.json (LPC.PC.7)")
' "$root/seeds/development_seeds.json" "$seed" 2>&1)" || refuse "${registry_message:-the seed registry check failed}"

out="$(cd "$caller" && realpath -m -- "$out_arg")"
runs_real="$(realpath -m "$root/runs")"
case "$out" in
    "$runs_real"/*) ;;
    *) refuse "out-dir must lie under $runs_real/ so that the GPU-hour tally sees every run" ;;
esac
meta="$out/$preset/run.meta.json"
if [ -e "$meta" ] || [ -L "$meta" ]; then
    refuse "$meta exists and must not be overwritten (it holds GPU hours)"
fi

threads="${LPC_THREADS:-4}"
[[ "$threads" =~ ^[1-9][0-9]?$ ]] || refuse "LPC_THREADS must be an integer from 1 to 99, got ${threads@Q}"

if [ -z "$device" ]; then
    if [ "$preset" = smoke ]; then device=cpu; else device=gpu; fi
fi
if [ "$device" = gpu ]; then platform=cuda; else platform=cpu; fi

if [ -n "${LPC_PYTHON:-}" ]; then
    py="$LPC_PYTHON"
elif [ -x "$root/.venv/bin/python" ]; then
    py="$root/.venv/bin/python"
else
    py=python3
fi

cd "$root" || exit 64
export OMP_NUM_THREADS="$threads" MKL_NUM_THREADS="$threads" OPENBLAS_NUM_THREADS="$threads"
# XLA's CPU client sizes its thread pools from PJRT_NPROC, then NPROC (plain environment variables
# read by getenv, not XLA flags, so they cannot abort XLA); unset it uses every schedulable CPU.
# Verified for jaxlib 0.11.2 in WU-0012.4. Never put a thread cap in XLA_FLAGS: an unknown entry aborts.
export PJRT_NPROC="$threads" NPROC="$threads"
export XLA_PYTHON_CLIENT_PREALLOCATE=false

# Lock first (cheap, exit 75 at once), then the tally while holding it, then the probe.
if [ "$preset" != smoke ] || [ "$device" = gpu ]; then
    { exec 9>>"$lock"; } 2>/dev/null || refuse "cannot open the GPU lock file ${lock@Q}"
    flock -n 9 || {
        echo "run_preset.sh: GPU busy (lock $lock is held): do other work (4.5)" >&2
        exit 75
    }
    if [ "$device" = gpu ]; then hours=12; else hours=0; fi
    if [ ! -f "$root/tools/gpu_hours.py" ]; then
        echo "run_preset.sh: tools/gpu_hours.py is missing: refusing to start (fail closed)" >&2
        exit 65
    fi
    python3 -I "$root/tools/gpu_hours.py" check --hours "$hours"
    tally=$?
    case "$tally" in
        0) ;;
        64 | 65) exit "$tally" ;;
        *)
            echo "run_preset.sh: the GPU-hour tally failed (exit $tally): refusing to start (fail closed)" >&2
            exit 65
            ;;
    esac
fi

probe="$(JAX_PLATFORMS=cpu timeout 120 "$py" -m lpcstudy --help 2>&1)" \
    || refuse "the CLI probe (python -m lpcstudy --help) failed"
seed_args=()
seed_flag=""
if grep -q -- '--seed-id' <<<"$probe"; then
    seed_args=(--seed-id "$seed")
    seed_flag="--seed-id $seed"
elif [ "$seed" = DEV-0 ]; then
    echo "note: the CLI has no --seed-id yet (WU-0001.1): DEV-0 runs with the CLI default seed 20261005"
else
    refuse "seed $seed needs the CLI flag --seed-id (WU-0001.1); only DEV-0 can run without it"
fi

command=(timeout --kill-after=300 12h "$py" -m lpcstudy --preset "$preset" --out "$out" "${seed_args[@]}")
if [ "${#systems[@]}" -ge 1 ]; then command+=(--systems "${systems[@]}"); fi
command+=("${passthrough[@]}")

export JAX_PLATFORMS="$platform"
mkdir -p "$out/$preset" || refuse "cannot create $out/$preset"
meta_call start "$meta" "$preset" "$seed" "$device" "$(date -u +%s)" "$seed_flag" "$threads" "$$" "${command[@]}" \
    || refuse "cannot write $meta"

if [ "$preset" = smoke ]; then
    run_recorded "$meta" "${command[@]}"
    exit "$?"
fi

# Background: a subshell of this already-checked front end (no second entry point). It inherits
# the lock on fd 9 and the validated argv, ignores SIGHUP like nohup, and outlives this process.
(
    ignore_hup=1
    trap '' HUP
    run_recorded "$meta" "${command[@]}"
) >"$out/$preset/console.log" 2>&1 </dev/null &
disown
echo "started pid=$! console=$out/$preset/console.log run_log=$out/$preset/run.log meta=$meta"
exit 0
