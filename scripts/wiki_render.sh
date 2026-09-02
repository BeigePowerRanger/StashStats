#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")/../quarto"
quarto render
echo "✓ Rendered to /mnt/ssd/Projects/BrainVault/Projects/StashStats/"
