#!/bin/bash

# DEV-COMMENT: This is the main build script for the entire J.A.R.V.I.S. application.
# It orchestrates the backend packaging, frontend build, and the final Tauri application bundling.

echo "🚀 Starting J.A.R.V.I.S. application build..."

# Step 1: Build the Python backend into an executable sidecar.
# This script calls PyInstaller to create the binary.
echo "📦 Packaging Python backend..."
./build_backend.sh

# Check if the backend build was successful
if [ $? -ne 0 ]; then
    echo "❌ Backend build failed. Aborting."
    exit 1
fi
echo "✅ Backend packaged successfully."


# Step 2: Build the frontend and bundle the Tauri application.
echo "🌐 Building frontend and Tauri bundle..."
./scripts/build_ui.sh

# Check if the UI build was successful
if [ $? -ne 0 ]; then
    echo "❌ Frontend/Tauri build failed. Aborting."
    exit 1
fi
echo "✅ Frontend/Tauri build completed."

echo "🎉 J.A.R.V.I.S. application build process finished."
echo "You would find the final application in 'src-tauri/target/release/bundle/'"
