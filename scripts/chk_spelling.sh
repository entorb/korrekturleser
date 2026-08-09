#!/bin/sh

# ensure we are in the root dir
cd "$(dirname "$0")/.."

if ! grep -qxF 'cspell-words-missing.txt' .gitignore; then
    echo "cspell-words-missing.txt missing from .gitignore"
    exit 1
fi

rm -f cspell-words-missing.txt
pnpm exec cspell-cli --cache --gitignore --quiet --unique .
if [ $? -ne 0 ]; then
    pnpm exec cspell-cli --cache --gitignore --unique --words-only . > cspell-words-missing.txt
    echo "See cspell-words-missing.txt for unknown words. Fix or transfer to cspell-words.txt"
    exit 1
fi
