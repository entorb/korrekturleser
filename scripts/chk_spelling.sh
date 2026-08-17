#!/bin/sh

# ensure we are in the root dir
cd "$(dirname "$0")/.."
# out=$(mktemp)
# trap 'rm -f "$out"' EXIT INT TERM

rm -f cspell-words-missing.txt
pnpm dlx cspell-cli@10.0.1 --unique --words-only . > cspell-words-missing.txt 2> /dev/null
status=$?

if [ $status -ne 0 ]; then
    echo "Found unknown spellings, see cspell-words-missing.txt. Fix or transfer to cspell-words.txt"
    head -n 100 "$out"
fi
exit $status
