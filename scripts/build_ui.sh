#!/bin/bash
set -e
# DEV-COMMENT: Build the React/Tauri frontend and bundle it with the Rust sidecar.
cd "$(dirname "$0")/../src-tauri"
npm install
npm run build
cargo tauri build
