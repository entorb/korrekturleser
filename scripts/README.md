# Helper Scripts

- `chk_*.sh` — exit 1 on failure. Slightly differ from CI ([check.yml](../.github/workflows/check.yml)): allowed to modify files locally. Non verbose output.
- `run_*.sh` — standalone use (start servers, run tools interactively).
- `run_checks.sh` — runs all `chk_*.sh` scripts, reports failures.
