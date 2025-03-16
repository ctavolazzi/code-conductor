# Testing Code Conductor

This directory contains tests for the Code Conductor application. The tests are designed to be simple, effective, and maintainable without complex dependencies.

## Testing Philosophy

We follow a pragmatic approach to testing that avoids complex imports and dependencies:

1. **Direct Testing**: Most tests directly interact with the code_conductor CLI and verify its output.
2. **File Access**: Tests may check file content or directory structures.
3. **Behavior Testing**: Tests focus on behavior rather than implementation details.

## Running Tests

To run all tests:

```bash
python3 -m pytest
```

To run a specific test file:

```bash
python3 -m pytest tests/test_version_simple.py
```

To run tests with verbose output:

```bash
python3 -m pytest -v
```

## Test Structure

Tests are organized by functionality:

- `test_simple.py`: Basic tests to verify the testing framework works.
- `test_version_simple.py`: Tests for version consistency.
- `test_edge_cases.py`: Tests for error handling and edge cases.
- `test_template.py`: Template for creating new tests.

## How to Write Tests

Tests are written using pytest. Each test file should contain test functions that start with `test_`.

### Example Test

```python
def test_something():
    """Test description here."""
    # Test setup
    proc = run_code_conductor(["some", "command"])

    # Assertions
    assert proc.returncode == 0, "Command should succeed"
    assert "expected output" in proc.stdout, "Output should contain expected text"
```

### Testing Approaches

We have three main approaches for testing, demonstrated in `test_template.py`:

1. **Direct File Access**: Reading files directly to test content.
2. **Subprocess Testing**: Running commands and checking output.
3. **Direct Imports**: For when you absolutely need to import modules.

## Testing Tips

1. **Keep Tests Simple**: Simple tests are easier to maintain and debug.
2. **Test Behavior, Not Implementation**: Focus on what the code does, not how it does it.
3. **Independent Tests**: Tests should not depend on each other.
4. **No Mock Everything**: Mock only what's necessary.
5. **Descriptive Names**: Use descriptive test names that indicate what's being tested.
6. **Good Assertions**: Error messages should be clear about what went wrong.

## Future Improvements

- Add more comprehensive tests for each command.
- Add tests for integration between commands.
- Add tests for the API.
- Add coverage reports.
- Integrate with CI/CD.