#!/bin/bash

echo "Building Assistant executable..."
echo ""

# Check if PyInstaller is installed
if ! python -m pip show pyinstaller > /dev/null 2>&1; then
    echo "PyInstaller not found. Installing..."
    python -m pip install pyinstaller
fi

echo ""
echo "Building executable..."
pyinstaller build.spec

echo ""
echo "Build complete!"
echo "Executable location: dist/assistant"

