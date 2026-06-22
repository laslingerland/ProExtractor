#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"
BIN_DIR="${HOME}/.local/bin"
COMMAND_PATH="${BIN_DIR}/proextractor"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is required." >&2
    exit 1
fi

PYTHON_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if ! python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 12))'; then
    echo "Error: Python 3.12 or newer is required; found ${PYTHON_VERSION}." >&2
    exit 1
fi

if ! python3 -m venv --help >/dev/null 2>&1; then
    echo "Error: Python venv support is unavailable. Install python3-venv or python3-full." >&2
    exit 1
fi

echo "Creating virtual environment in ${VENV_DIR}"
python3 -m venv --system-site-packages "${VENV_DIR}"

echo "Installing ProExtractor"
"${VENV_DIR}/bin/python" -m pip install \
    --disable-pip-version-check \
    --no-deps \
    --no-build-isolation \
    --editable "${PROJECT_DIR}"

mkdir -p "${BIN_DIR}"

if [[ -e "${COMMAND_PATH}" && ! -L "${COMMAND_PATH}" ]]; then
    echo "Error: ${COMMAND_PATH} already exists and is not a symbolic link." >&2
    exit 1
fi

ln -sfn "${VENV_DIR}/bin/proextractor" "${COMMAND_PATH}"

echo
echo "ProExtractor installed successfully."
echo "Command: ${COMMAND_PATH}"

case ":${PATH}:" in
    *":${BIN_DIR}:"*)
        echo "Run: proextractor --help"
        ;;
    *)
        echo "Add this line to your shell configuration, then open a new terminal:"
        echo "  export PATH=\"\${HOME}/.local/bin:\${PATH}\""
        echo "For now, run: ${COMMAND_PATH} --help"
        ;;
esac

