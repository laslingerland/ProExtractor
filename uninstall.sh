#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"
COMMAND_PATH="${HOME}/.local/bin/proextractor"
EXPECTED_TARGET="${VENV_DIR}/bin/proextractor"
DATABASE_PATH="${PROJECT_DIR}/data/songs.sqlite"

if [[ -L "${COMMAND_PATH}" ]]; then
    CURRENT_TARGET="$(readlink -- "${COMMAND_PATH}")"
    if [[ "${CURRENT_TARGET}" == "${EXPECTED_TARGET}" ]]; then
        rm -- "${COMMAND_PATH}"
        echo "Removed ${COMMAND_PATH}"
    else
        echo "Kept ${COMMAND_PATH}: it points to another installation." >&2
    fi
elif [[ -e "${COMMAND_PATH}" ]]; then
    echo "Kept ${COMMAND_PATH}: it is not a symbolic link." >&2
fi

if [[ -d "${VENV_DIR}" ]]; then
    rm -rf -- "${VENV_DIR}"
    echo "Removed ${VENV_DIR}"
fi

echo "ProExtractor uninstalled."
if [[ -f "${DATABASE_PATH}" ]]; then
    echo "Your SQLite database was kept at: ${DATABASE_PATH}"
else
    echo "No default SQLite database was found. Its expected location is: ${DATABASE_PATH}"
fi
echo "Source files and databases were not removed."
