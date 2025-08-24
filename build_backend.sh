#!/bin/bash

# DEV-COMMENT: This script is responsible for packaging the Python backend
# into a single executable file that can be bundled with the Tauri application
# as a sidecar. This is a crucial step for creating a self-contained desktop app.

# Exit immediately if a command exits with a non-zero status.
set -e

# Define the name for our executable
OUTPUT_NAME="main"

# Define the path to our main Python script
APP_SCRIPT="app/main.py"

# Define the target directory for the binary
# This must match the 'externalBin' path in tauri.conf.json
TARGET_DIR="src-tauri/bin"

# Create the target directory if it doesn't exist
mkdir -p $TARGET_DIR

# Run PyInstaller
# --name: The name of the executable.
# --onefile: Bundle everything into a single executable file.
# --distpath: The directory to place the final executable in.
# --workpath: A temporary directory for build files.
# --specpath: Where to put the .spec file.
# --clean: Clean PyInstaller cache and remove temporary files before building.
# --noconfirm: Don't ask for confirmation if output files already exist.
# --hidden-import: Explicitly include packages that PyInstaller might miss.
#                  Uvicorn's standard workers are often missed.
pyinstaller \
    --name $OUTPUT_NAME \
    --onefile \
    --distpath $TARGET_DIR \
    --workpath build/pyinstaller \
    --specpath build \
    --clean \
    --noconfirm \
    --hidden-import "uvicorn.logging" \
    --hidden-import "uvicorn.loops" \
    --hidden-import "uvicorn.protocols" \
    $APP_SCRIPT

# Clean up build artifacts we don't need
rm -rf build

echo "✅ Backend executable successfully built at $TARGET_DIR/$OUTPUT_NAME"
