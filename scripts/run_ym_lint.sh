#!/bin/sh
set -e
cd "$(dirname "$0")/.."

# included in prek, so changed file prefix from chk_ to run_

out=$(mktemp)
trap 'rm -f "$out"' EXIT INT TERM

status=0
uvx --no-build ryl@0.21.0 check -d '{extends: default, rules: {line-length: disable, truthy: disable}, ignore: [pnpm-lock.yaml]}' . --fix >"$out" 2>&1 || status=$?

if [ $status -ne 0 ]; then
  head -n 100 "$out"
else
  echo OK
fi
exit $status
