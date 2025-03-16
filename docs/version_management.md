# Version Management in Code Conductor

## Overview

Code Conductor uses a centralized version management approach where the version number is defined in a single location and referenced throughout the codebase. This ensures consistency and simplifies the release process.

## Implementation Details

### Single Source of Truth

The root package `__init__.py` file serves as the single source of truth for the version:

```python
# code_conductor/__init__.py
__version__ = "0.4.5"
```

### Importing the Version

All modules that need the version import it from the root package:

```python
# Any module that needs the version
from code_conductor import __version__
```

### Build System Integration

The `setup.py` file dynamically reads the version from the root package:

```python
# setup.py
import re

# Get version from root package __init__.py
with open('code_conductor/__init__.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

setup(
    name="code-conductor",
    version=version,
    # ...
)
```

The build script also reads the version dynamically:

```bash
# build_and_upload.sh
VERSION=$(grep -oP '__version__ = "\K[^"]+' code_conductor/__init__.py)
echo "Building code-conductor v${VERSION} package..."
```

## Version Testing

A comprehensive test suite ensures that the version is consistent across all modules:

```python
# tests/test_version.py
import code_conductor

def test_submodule_versions_match_root():
    import code_conductor.work_efforts.core
    self.assertEqual(code_conductor.work_efforts.core.__version__, code_conductor.__version__)
    # ... more assertions for other modules
```

## Release Process

When releasing a new version of Code Conductor:

1. **Update the Version**: Change the version number in `code_conductor/__init__.py`
   ```python
   __version__ = "0.4.6"  # Example version bump
   ```

2. **Run the Version Tests**: Ensure all version references are consistent
   ```bash
   python -m unittest tests/test_version.py
   ```

3. **Update Changelog**: Document the changes in CHANGELOG.md

4. **Build and Upload**: Run the build script to create and upload the package
   ```bash
   ./build_and_upload.sh
   ```

## Benefits

This centralized approach provides several benefits:

1. **Consistency**: All parts of the codebase use the same version number
2. **Maintainability**: Only one place needs to be updated when releasing a new version
3. **Testability**: Tests can verify that version numbers are consistent
4. **Automation**: Build processes can use the version without hardcoding

## Version Format

Code Conductor follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible new features
- **PATCH**: Backward-compatible bug fixes

Example: `0.4.5` where `0` is MAJOR, `4` is MINOR, and `5` is PATCH.