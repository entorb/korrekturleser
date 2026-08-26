#!/usr/bin/env python3
"""
Print packages to remove/re-add for a `latest-version` dependency update.

Reads pyproject.toml's `project.dependencies` and `dependency-groups.dev`
lists and prints four lines:
  1) bare names to pass to `uv remove`             (extras/version stripped)
  2) name[extra] specs to pass to `uv add`         (version stripped, extras kept)
  3) bare names to pass to `uv remove --dev`       (extras/version stripped)
  4) name[extra] specs to pass to `uv add --dev`   (version stripped, extras kept)

Exact-pinned entries (e.g. "pandas==2.2.3") and direct references
(e.g. "pkg @ git+https://...") are skipped on all lines, so they are
left untouched in pyproject.toml.
"""

import re
import tomllib
from pathlib import Path

FILE = Path("pyproject.toml")
RE_NAME = re.compile(r"^([A-Za-z0-9_.-]+)(\[[^\]]*\])?")


def extract(deps: list) -> tuple[str, str]:
    """Return (remove_names, add_specs) as space-joined strings."""
    remove_names = []
    add_specs = []
    for dep in deps:
        if not isinstance(dep, str):
            continue  # e.g. PEP 735 {include-group = ...} entries
        main_part = dep.split(";", 1)[0]  # drop environment marker
        if "==" in main_part or "@" in main_part:
            continue  # exact pin or direct reference (URL/VCS/path): leave untouched
        match = RE_NAME.match(main_part)
        if not match:
            continue
        name, extra = match.group(1), match.group(2) or ""
        remove_names.append(name)
        add_specs.append(name + extra)
    return " ".join(remove_names), " ".join(add_specs)


def main() -> None:  # noqa: D103
    with FILE.open("rb") as f:
        toml = tomllib.load(f)

    dep_remove, dep_add = extract(toml["project"]["dependencies"])
    dev_remove, dev_add = extract(toml["dependency-groups"]["dev"])

    print(dep_remove)
    print(dep_add)
    print(dev_remove)
    print(dev_add)


if __name__ == "__main__":
    main()
