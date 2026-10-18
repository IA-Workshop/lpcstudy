P=${LPC_PYTHON:-python}
for phi in 0 0.3; do
  for c in C1 C8 C2 C4 C5; do $P m2_coverage.py $c $phi 40000; done
  for c in C3 C9 C7; do $P m2_coverage.py $c $phi 20000; done
  $P m2_coverage.py C6 $phi 10000
done
for phi in 0.1 0.2; do $P m2_coverage.py C1 $phi 20000; done
for c in C2 C4; do for kw in '{"sigma":1.5,"c":0.8}' '{"sigma":2.0,"c":0.8}' '{"sigma":1.5,"c":0.95}' '{"sigma":2.0,"c":0.95}'; do
  t=$(echo $kw | tr -d '{}":, '); $P m2_coverage.py $c 0 20000 _$t "$kw"; done; done
