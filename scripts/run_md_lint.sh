#!/bin/sh

# included in prek, so changed file prefix from chk_ to run_

cd "$(dirname "$0")/.." || exit 1
out=$(mktemp)
trap 'rm -f "$out"' EXIT INT TERM

rumdl fmt .
rumdl check . >"$out" 2>&1
status=$?

if [ $status -ne 0 ]; then
  printf 'Issues remaining, you can try:\nrumdl check . --fix\n'
  head -n 100 "$out"
else
  echo OK
fi
exit $status
