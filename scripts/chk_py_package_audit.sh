#!/bin/sh
set -e
cd "$(dirname "$0")/.."

out=$(mktemp)
trap 'rm -f "$out"' EXIT INT TERM

status=0
# TODO: pyarrow PYSEC-2026-113 fixed in 23.0.1, prod does not support it yet; drop ignore once migrated
uv audit --preview-features audit --ignore PYSEC-2026-113 >"$out" 2>&1 || status=$?

# print output in good case only if more than 2 lines
if [ $status -eq 0 ]; then
  lines=$(wc -l <"$out")
  if [ "$lines" -gt 2 ]; then
    head -n 10 "$out"
  fi
  echo OK
else
  head -n 100 "$out"
fi
exit $status
