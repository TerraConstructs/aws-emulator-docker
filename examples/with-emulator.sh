#!/usr/bin/env bash
# Run a command with a fresh AWS Emulator, then stop the emulator.
#
# Usage: examples/with-emulator.sh <command> [args...]
# Example: EMULATOR_PORT=19701 examples/with-emulator.sh examples/python/run-tests.sh
#
# See .github/actions/aws-emulator/start-emulator.sh for the settings. That file
# is a copy of start-emulator.sh from https://github.com/xSAVIKx/run-aws-emulator
# at the release that .github/workflows/examples.yml uses. CI checks the copy.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
start="$here/../.github/actions/aws-emulator/start-emulator.sh"

# A separate assignment keeps the exit status of the script visible to set -e.
out="$("$start")"
eval "$out"
trap '"$start" --stop' EXIT
"$@"
