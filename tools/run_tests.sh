#!/usr/bin/env bash
# Run pytest for one tier under the test and compute discipline of DEVELOPMENT_WORKFLOW.md 4.5.
#
# Usage: tools/run_tests.sh <tier> [--lf] [--tb=long] [--durations=N] [--background] <path>...
#
#   tier   unit | integration | slow | gpu
#   path   a file or directory under tests/<tier>, optionally with a ::node id.
#          Relative paths are taken from the caller's directory.
#
# Refusals (exit 64, one line on stderr): an unknown tier, a missing or wrong-tier path,
# no path, a whole-suite path (tests, tests/, .), any other flag (-n, -s, -v, ...), a bad
# LPC_THREADS (not 1..99) or LPC_GPU_WAIT (not 0..30). The wrapper is its own whole-suite guard,
# because the hook .claude/hooks/test_gate.py does not see inside it. A gate runs one call
# per tier: LPC_GATE=merge tools/run_tests.sh unit tests/unit
#
# Environment (set here, overriding what is inherited): JAX_PLATFORMS=cpu (cuda,cpu for gpu),
# XLA_PYTHON_CLIENT_PREALLOCATE=false, OMP/MKL/OPENBLAS_NUM_THREADS=$LPC_THREADS (default 4) and
# PJRT_NPROC=NPROC=$LPC_THREADS (the XLA CPU thread pools). XLA_FLAGS is never set or altered.
# LPC_PYTHON selects the interpreter (else <root>/.venv/bin/python, else python3).
# LPC_GPU_LOCK is the lock file (default /tmp/lpcstudy-gpu.lock); LPC_GPU_WAIT shortens the wait.
#
# Timeouts (4.5): unit 300 s, integration 900 s, slow 3600 s, gpu 1800 s, then SIGKILL after 30 s.
# Exit codes: 64 usage or refusal, 75 GPU lock busy, 124 timeout (137 if it had to be killed),
# otherwise pytest's code. PYTEST_ADDOPTS and PYTEST_PLUGINS must be unset (64).
#
# --background (for slow and gpu): runs detached, logs to runs/tests/<tier>-<UTC stamp>.log and
# writes the exit code to <log>.exit; prints "pid=... log=..." and exits 0.

set -u

caller="$PWD"
self="$(realpath "${BASH_SOURCE[0]}")"
root="$(cd "$(dirname "$self")/.." && pwd -P)"

refuse() {
    echo "run_tests.sh: refused: $1" >&2
    exit 64
}

[ "$#" -ge 1 ] || refuse "usage: run_tests.sh <unit|integration|slow|gpu> [--lf] [--tb=long] [--durations=N] [--background] <path>..."
tier="$1"
shift
case "$tier" in
    unit) limit=300 ;;
    integration) limit=900 ;;
    slow) limit=3600 ;;
    gpu) limit=1800 ;;
    *) refuse "unknown tier '$tier' (unit, integration, slow or gpu)" ;;
esac

# pytest also reads options and plugins from the environment, past the argument whitelist below.
[ -z "${PYTEST_ADDOPTS:-}" ] || refuse "PYTEST_ADDOPTS is set; unset it (options are whitelisted, 4.6)"
[ -z "${PYTEST_PLUGINS:-}" ] || refuse "PYTEST_PLUGINS is set; unset it (no extra plugins, 4.6)"

threads="${LPC_THREADS:-4}"
[[ "$threads" =~ ^[1-9][0-9]?$ ]] || refuse "LPC_THREADS must be an integer from 1 to 99, got '$threads'"
wait_s="${LPC_GPU_WAIT:-30}"
[[ "$wait_s" =~ ^[0-9]{1,2}$ ]] && [ "$((10#$wait_s))" -le 30 ] \
    || refuse "LPC_GPU_WAIT must be an integer from 0 to 30, got '$wait_s'"
wait_s="$((10#$wait_s))"

extras=()
paths=()
background=0
for arg in "$@"; do
    case "$arg" in
        --lf | --tb=long) extras+=("$arg") ;;
        --durations=*)
            [[ "${arg#--durations=}" =~ ^[0-9]+$ ]] || refuse "bad option '$arg' (use --durations=N)"
            extras+=("$arg")
            ;;
        --background) background=1 ;;
        -*) refuse "option '$arg' is not allowed (only --lf, --tb=long, --durations=N, --background)" ;;
        *)
            [ -n "$arg" ] || refuse "empty path"
            file="${arg%%::*}"
            [ -n "$file" ] || refuse "empty path in '$arg'"
            absolute="$(cd "$caller" && realpath -m -- "$file")"
            case "$absolute" in
                "$root/tests/$tier" | "$root/tests/$tier"/*) ;;
                *) refuse "path '$arg' is not tests/$tier or under it (whole-suite and wrong-tier paths are refused)" ;;
            esac
            [ -e "$absolute" ] || refuse "path '$file' does not exist"
            paths+=("${absolute#"$root"/}${arg:${#file}}")
            ;;
    esac
done
[ "${#paths[@]}" -ge 1 ] || refuse "no test path given (tests/$tier/... is required)"

cd "$root" || exit 64

if [ "$background" -eq 1 ]; then
    mkdir -p "$root/runs/tests"
    stamp="$(date -u +%Y%m%dT%H%M%SZ)"
    log="$root/runs/tests/$tier-$stamp.log"
    [ ! -e "$log" ] || log="$root/runs/tests/$tier-$stamp-$$.log"
    nohup bash -c '"$@"; echo "$?" >"$0.exit"' "$log" "$self" "$tier" "${extras[@]}" "${paths[@]}" \
        >"$log" 2>&1 </dev/null &
    echo "pid=$! log=$log"
    exit 0
fi

if [ -n "${LPC_PYTHON:-}" ]; then
    py="$LPC_PYTHON"
elif [ -x "$root/.venv/bin/python" ]; then
    py="$root/.venv/bin/python"
else
    py=python3
fi

export OMP_NUM_THREADS="$threads" MKL_NUM_THREADS="$threads" OPENBLAS_NUM_THREADS="$threads"
# XLA's CPU client sizes its thread pools from PJRT_NPROC, then NPROC (plain environment variables
# read by getenv, not XLA flags, so they cannot abort XLA); unset it uses every schedulable CPU.
# Verified for jaxlib 0.11.2 in WU-0012.4. Never put a thread cap in XLA_FLAGS: an unknown entry aborts.
export PJRT_NPROC="$threads" NPROC="$threads"
export XLA_PYTHON_CLIENT_PREALLOCATE=false
if [ "$tier" = gpu ]; then
    export JAX_PLATFORMS=cuda,cpu
    lock="${LPC_GPU_LOCK:-/tmp/lpcstudy-gpu.lock}"
    { exec 9>>"$lock"; } 2>/dev/null || refuse "cannot open the GPU lock file '$lock'"
    flock -w "$wait_s" 9 || {
        echo "run_tests.sh: GPU busy (lock '$lock' held for ${wait_s} s): do other work (4.5)" >&2
        exit 75
    }
else
    export JAX_PLATFORMS=cpu
fi

started="$SECONDS"
timeout --kill-after=30 "$limit" "$py" -m pytest -q --tb=short -rfE "${extras[@]}" "${paths[@]}"
code=$?
if [ "$code" -eq 124 ]; then
    echo "TIMEOUT after $limit s (4.5): investigate, do not raise" >&2
elif [ "$code" -eq 137 ]; then
    echo "TIMEOUT (exit 137, SIGKILL) after $((SECONDS - started)) s; the limit is $limit s plus a 30 s kill grace (4.5), an external kill gives the same code: investigate, do not raise" >&2
fi
exit "$code"
