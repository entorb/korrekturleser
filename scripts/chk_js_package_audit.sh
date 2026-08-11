#!/bin/sh

# ensure we are in the root dir
cd "$(dirname "$0")/.."

if pnpm audit; then
    exit 0
fi

if pnpm audit --fix update && pnpm audit; then
    echo "Fixed: pnpm-lock.yaml updated."
    exit 0
fi

if pnpm audit --fix override && pnpm install --ignore-scripts && pnpm audit; then
    echo "Fixed: overrides added to pnpm-workspace.yaml."
    exit 0
fi

echo "Audit issues remain. Inspect: pnpm audit"
exit 1
