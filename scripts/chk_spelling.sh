#!/bin/sh

# ensure we are in the root dir
cd "$(dirname "$0")/.."

rm -f cspell-words-missing.txt
pnpm dlx cspell-cli@10.0.1 --cache --gitignore --quiet --unique .
if [ $? -ne 0 ]; then
    pnpm dlx cspell-cli@10.0.1 --cache --gitignore --unique --words-only . > cspell-words-missing.txt
    echo "See cspell-words-missing.txt for unknown words. Fix or transfer to cspell-words.txt"
    exit 1
fi
