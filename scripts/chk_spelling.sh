#!/bin/sh

# ensure we are in the root dir
cd "$(dirname "$0")/.."
out=$(mktemp)
trap 'rm -f "$out"' EXIT INT TERM

rm -f cspell-words-missing.txt
pnpm dlx cspell-cli@10.0.1 --cache --gitignore --quiet --unique . >"$out" 2>&1
status=$?

if [ $status -ne 0 ]; then
    pnpm dlx cspell-cli@10.0.1 --cache --gitignore --unique --words-only . > cspell-words-missing.txt 2>>"$out"
    echo "See cspell-words-missing.txt for unknown words. Fix or transfer to cspell-words.txt"
    head -n 100 "$out"
fi
exit $status
