#!/bin/bash

# Build and upload script for code-conductor

# Get version from __init__.py
VERSION=$(grep "__version__ = " __init__.py | cut -d '"' -f 2)
echo "Building code-conductor v${VERSION} package..."

# Clean up previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m pip install --upgrade build
python -m build

echo "Build complete. Package files:"
ls -la dist/

echo "Ready to upload to PyPI"
echo "To upload, run: python -m twine upload dist/*"
echo ""
echo "Make sure you have twine installed: pip install twine"
echo "If you need a test upload first, run: python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*"
echo ""
echo "After uploading, you can verify the installation with: pip install --upgrade code-conductor"