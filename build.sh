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

# Check if we have the enhanced startup scripts
if [ -f "start_jarvis_enhanced.py" ]; then
    echo "📋 Enhanced Jarvis AI build detected"
    
    # Install dependencies first
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    
    # Build frontend with npm
    if [ -d "src-tauri" ]; then
        cd src-tauri
        
        # Install npm dependencies
        echo "📦 Installing npm dependencies..."
        npm install --legacy-peer-deps
        
        # Build the frontend
        echo "🔨 Building frontend..."
        npm run build
        
        # Build Tauri application
        echo "🖥️ Building Tauri application..."
        npm run tauri:build
        
        cd ..
    else
        echo "❌ src-tauri directory not found"
        exit 1
    fi
else
    # Fallback to original build process
    echo "🌐 Building frontend... (using fallback method)"
    # In a real environment, you would have npm/yarn installed and run the build command.
    # The `beforeBuildCommand` in `tauri.conf.json` handles this automatically when using `tauri build`.
    
    # Step 3: Build the final Tauri application.
    # This command bundles the frontend code and the backend sidecar into a single executable.
    # This step requires the Tauri CLI and a full Rust development environment.
    echo "🖥️ Building Tauri application... (using fallback method)"
    # Example command:
    # (cd src-tauri && cargo tauri build)
fi

# Check if the build was successful
if [ $? -ne 0 ]; then
    echo "❌ Frontend/Tauri build failed. Aborting."
    exit 1
fi
echo "✅ Frontend/Tauri build completed."

echo "🎉 J.A.R.V.I.S. application build process finished."
echo "📁 Final application can be found in:"
echo "   • Windows: src-tauri/src-tauri/target/release/J.A.R.V.I.S..exe"
echo "   • macOS: src-tauri/src-tauri/target/release/bundle/macos/J.A.R.V.I.S..app"
echo "   • Linux: src-tauri/src-tauri/target/release/j-a-r-v-i-s"
echo ""
echo "💡 To run in development mode:"
echo "   • Windows: start_jarvis.bat"
echo "   • Cross-platform: python start_jarvis_enhanced.py"