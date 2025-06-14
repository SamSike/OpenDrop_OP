# Testing Guide

This project uses `pytest` as the main testing framework. All test cases are located in the same level of directory as the corresponding test object. A unified entry point `test_all.py` is provided to run all core module tests.

## 1. Environment Setup

Follow the setup guide in [README.md](./README.md) to complete the environment setup.

## 2. Run All Tests

Use the following command to execute all tests:

```bash
python test_all.py
```

### Output Example

```text
test_YL_fit (test_BA_fit.TestBAFit) ... ok
test_cluster_OPTICS (test_polynomial_fit.TestPolynomialFit) ... ok
...
Ran 33 tests in 4.05s

OK
```

## 3. Run a Specific Module Test (for debugging)

You can also run a specific test file using:

```bash
pytest tests/test_polynomial_fit.py
```
