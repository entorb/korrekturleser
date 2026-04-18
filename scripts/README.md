# Helper Scripts

- `chk_*.sh` — code checks. exit 1 on failure. Slightly different from CI ([check.yml](../.github/workflows/check.yml)): here allowed to modify files. Non verbose output.
- `run_*.sh` — standalone use (start servers, run tools interactively).
- `run_checks.sh` — runs all `chk_*.sh` scripts, reports failures.
