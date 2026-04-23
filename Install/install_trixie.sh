#!/bin/bash
# Shim: delegates to the canonical install script in Software/Python/gopigo3/scripts/

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="$SCRIPT_DIR/../Software/Python/gopigo3/scripts/install_trixie.sh"

if [ ! -f "$TARGET" ]; then
    echo "Error: could not find $TARGET" >&2
    exit 1
fi

# Preserve sourcing behaviour so venv activation propagates to the caller's shell
if [ "${BASH_SOURCE[0]}" != "$0" ]; then
    source "$TARGET"
else
    bash "$TARGET" "$@"
fi
