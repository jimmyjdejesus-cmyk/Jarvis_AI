
Copyright (c) 2025 Jimmy De Jesus (Bravetto)

Licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0).
See https://creativecommons.org/licenses/by/4.0/ for license terms.

#!/usr/bin/env bash
set -euo pipefail

# Generate a reproducible requirements lock file from the top-level requirements
# Uses pip-compile from pip-tools to pin transitive deps

if ! command -v pip-compile >/dev/null 2>&1; then
  echo "pip-compile not found; installing pip-tools temporarily"
  python -m pip install --upgrade pip
  python -m pip install pip-tools
fi

echo "Generating requirements.lock from requirements.txt"
pip-compile --output-file=requirements.lock requirements.txt
echo "requirements.lock generated"

if command -v uv >/dev/null 2>&1; then
  echo "Updating uv.lock via uv lock"
  uv lock --no-progress
  echo "uv.lock updated"
else
  echo "uv not found; skipping uv.lock generation (run 'uv lock' locally or in CI)"
fi
