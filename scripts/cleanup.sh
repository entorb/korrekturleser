#!/bin/sh
cd $(dirname $0)/..

rm -f .DS_Store .coverage .cspellcache .eslintcache coverage.xml
rm -rf coverage coverage_report .ruff_cache dist/*
