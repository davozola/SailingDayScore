#!/bin/bash
set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Navigate to frontend directory
cd "$SCRIPT_DIR/frontend"

# Install and build
npm install
npm run build

echo "Build completed successfully"
ls -la dist/
