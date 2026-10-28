#!/bin/bash
while pgrep -f "diag.py lorenz96_4" >/dev/null; do sleep 20; done
H=/home/brianm/projects/physics/chaos/lpcstudy-wt/wu/0037-v7-diagnosis/docs/agent/notes/2026-10-25-v7-diagnosis
$H/run_chain.sh /tmp/claude-1000/-home-brianm-projects-physics-chaos-lpcstudy/48caab16-c921-41c4-aaa2-2238d7e5cbaa/scratchpad/v7/main 2 "hindmarsh_rose:60 hyper_jha:60" &
$H/run_chain.sh /tmp/claude-1000/-home-brianm-projects-physics-chaos-lpcstudy/48caab16-c921-41c4-aaa2-2238d7e5cbaa/scratchpad/v7/main 3 "lorenz63_r166:100 rossler_z:150 lorenz63:100 rossler_hyper:40" &
wait
