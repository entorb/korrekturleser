#!/bin/sh

# ensure we are in the root dir
cd "$(dirname "$0")/.."
out=$(mktemp)
trap 'rm -f "$out"' EXIT INT TERM

if pnpm audit >"$out" 2>&1; then
    exit 0
fi

if pnpm audit --fix=update >"$out" 2>&1 && pnpm audit >"$out" 2>&1; then
    echo "Fixed: pnpm-lock.yaml updated."
    exit 0
fi

if pnpm audit --fix=override >>"$out" 2>&1 && pnpm install --ignore-scripts >>"$out" 2>&1 && pnpm audit >"$out" 2>&1; then
    echo "Fixed: overrides added to pnpm-workspace.yaml."
    exit 0
fi

echo "Audit issues remain. Inspect: pnpm audit"
tail -n 100 "$out"
exit 1
