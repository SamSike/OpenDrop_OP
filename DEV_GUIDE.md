# Developer Guide: opendrop_ml

## Table of Contents

-   [Developer Guide: opendrop_ml](#developer-guide-opendrop_ml)
    -   [Table of Contents](#table-of-contents)
    -   [1. Introduction](#1-introduction)
        -   [What You'll Learn](#what-youll-learn)
    -   [2. Setup Instructions](#2-setup-instructions)
    -   [3. Project Structure](#3-project-structure)
        -   [3.1. High-Level Overview](#31-high-level-overview)
        -   [3.2. Directory Structure](#32-directory-structure)
        -   [3.3. Backend Architecture (`modules/`)](#33-backend-architecture-modules)
            -   [Core Components](#core-components)
            -   [Analysis Pipelines](#analysis-pipelines)
            -   [Data Flow](#data-flow)
        -   [3.4. Frontend Architecture (`views/`)](#34-frontend-architecture-views)
            -   [Framework \& Navigation](#framework--navigation)
            -   [Shared State Management](#shared-state-management)
            -   [Workflow Pages](#workflow-pages)
            -   [Reusable Components](#reusable-components)
    -   [4. Contribution Workflow](#4-contribution-workflow)
        -   [4.1. Branching Strategy](#41-branching-strategy)
            -   [Main Branches](#main-branches)
            -   [Development Branches](#development-branches)
            -   [Feature Branch Workflow](#feature-branch-workflow)
        -   [4.2. Pull Request (PR) Process](#42-pull-request-pr-process)
            -   [PR Requirements](#pr-requirements)
        -   [4.3. Code Review Guidelines](#43-code-review-guidelines)
            -   [Review Focus Areas](#review-focus-areas)
            -   [Best Practices](#best-practices)
    -   [5. Coding Standards](#5-coding-standards)
        -   [5.1. Python Style Guide](#51-python-style-guide)
            -   [Core Standards](#core-standards)
            -   [Documentation Requirements](#documentation-requirements)
            -   [Example Docstring](#example-docstring)
            -   [Linting Guide](#linting-guide)
        -   [5.2. Commit Message Convention](#52-commit-message-convention)
            -   [Angular Convention Format](#angular-convention-format)
            -   [Commit Types](#commit-types)
            -   [Examples](#examples)
        -   [5.3. Frontend Standards (CustomTkinter)](#53-frontend-standards-customtkinter)
            -   [UI Guidelines](#ui-guidelines)
            -   [Component Structure](#component-structure)
    -   [6. Testing Procedures](#6-testing-procedures)
        -   [6.1. Testing Overview](#61-testing-overview)
            -   [Framework \& Structure](#framework--structure)
            -   [Test File Examples](#test-file-examples)
        -   [6.2. Writing Tests](#62-writing-tests)
            -   [Test Types](#test-types)
            -   [Naming Conventions](#naming-conventions)
            -   [Example Test Structure](#example-test-structure)
        -   [6.3. Running Tests](#63-running-tests)
            -   [Basic Commands](#basic-commands)
            -   [Specific Test Execution](#specific-test-execution)
            -   [Test Coverage](#test-coverage)
        -   [6.4. Test Development Guidelines](#64-test-development-guidelines)
            -   [Best Practices](#best-practices-1)
            -   [Coverage Goals](#coverage-goals)
    -   [7. Deployment Guidelines](#7-deployment-guidelines)
        -   [7.1. Building Cython Extensions](#71-building-cython-extensions)
            -   [Prerequisites for C++ Modules](#prerequisites-for-c-modules)
            -   [Build Command](#build-command)
            -   [What This Does](#what-this-does)
        -   [7.2. Core Packaging with `setup.py`](#72-core-packaging-with-setuppy)
            -   [Setup.py Responsibilities](#setuppy-responsibilities)
            -   [Platform-Specific Libraries](#platform-specific-libraries)
            -   [Compiler Configuration](#compiler-configuration)
        -   [7.3. Deployment Considerations](#73-deployment-considerations)
            -   [Cross-Platform Builds](#cross-platform-builds)
            -   [Packaging Checklist](#packaging-checklist)
            -   [Common Packaging Tools](#common-packaging-tools)
            -   [Example PyInstaller Command](#example-pyinstaller-command)
        -   [7.4. Testing Packaged Applications](#74-testing-packaged-applications)
            -   [Validation Steps](#validation-steps)
            -   [Platform Testing Matrix](#platform-testing-matrix)
    -   [8. Further Information](#8-further-information)
        -   [8.1. Configuration \& Customization](#81-configuration--customization)
        -   [8.2. Resources \& Support](#82-resources--support)
            -   [Documentation](#documentation)
            -   [Troubleshooting](#troubleshooting)
            -   [Quick Navigation](#quick-navigation)

---

## 1. Introduction

Welcome to the **opendrop_ml Developer Guide**!

**opendrop_ml** is an open-source, cross-platform software for analyzing liquid droplets in surface science using contact angle and pendant drop (interfacial tension) methods. It integrates classical computer vision techniques with machine learning (ML)-based analysis (Conan-ML), offering both flexibility and automation for scientific users.

### What You'll Learn

This guide provides all the necessary information for developers to:

-   Set up their development environment
-   Understand the project architecture
-   Contribute effectively to the codebase
-   Adhere to project standards and best practices

## 2. Setup Instructions

Setting up the development environment for opendrop_ml involves installing Python, cloning the repository, and installing dependencies. Please check the installation guide in [README file](./README.md).

## 3. Project Structure

opendrop_ml follows a **modular architecture** to separate concerns and facilitate extensibility.

### 3.1. High-Level Overview

![High-Level Architecture](opendrop_ml/assets/high-level-project-diagram.png)

The project is primarily divided into:

-   **Backend Logic** (`modules/`)
-   **Frontend UI** (`views/`)
-   **Utility Functions** (`utils/`)

The test modules follow the same folder structure. The `tests/` folder is located in the project root folder.

### 3.2. Directory Structure

```
OpenDrop_OP/
├── opendrop_ml/                  # Main Python package containing all logic and UI
│   ├── modules/                # Core backend logic, organized by functionality
│   │   ├── contact_angle/      # CA specific processing
│   │   ├── core/               # Core classes (ExperimentalSetup, DropData)
│   │   ├── fitting/            # Fitting algorithms (BA_fit, ellipse_fit, etc.)
│   │   ├── ift/                # IFT specific processing, including Cython extensions
│   │   │   ├── younglaplace/   # Young-Laplace fitting
│   │   │   └── hough/          # Hough transform utilities
│   │   ├── image/              # Image processing utilities
│   │   ├── ML_model/           # TensorFlow model, input-output conversion (Conan-ML)
│   │   └── preprocessing/      # Image preprocessing steps
│   ├── views/                  # Frontend UI (CustomTkinter)
│   │   ├── helper/             # Helper modules for building UI components and layout logic
│   │   └── component/          # Reusable UI widgets
│   ├── utils/                  # Helper code (config, validation, image IO, enums)
│   ├── assets/                 # Static assets like images and fonts
│   ├── experimental_data_set/  # Example input images for testing and demonstration
│   ├── dependencies/           # External library dependencies for C++ modules
│   ├── main.py                 # Main entry point for launching the opendrop_ml GUI
│   └── user_config.yaml        # User-specific configuration and preferences
├── pyproject.toml              # Build system and metadata (PEP 518); modern alternative to setup.py
├── setup.py                    # Python package installer script
├── install.py                  # Custom installation script (e.g., dependency handling, setup)
├── test_all.py                 # Entry point to run all unit tests in the codebase
├── requirements.txt            # List of required Python packages
├── windows-installer.wxs       # WiX Toolset script for creating a Windows installer
├── TESTING.md                  # Guide for running tests using test_all.py
├── RELEASE.md                  # Release notes and changelog for each version
├── DEV_GUIDE.md                # Developer setup and contribution guide
└── README.md                   # Overview of the project, how to install and use it
```

### 3.3. Backend Architecture (`modules/`)

#### Core Components

| Component              | File                        | Description                                                                        |
| ---------------------- | --------------------------- | ---------------------------------------------------------------------------------- |
| **Entry Point**        | `main.py`                   | Initializes and runs the application                                               |
| **Data Structures**    | `modules/core/classes.py`   | Defines `ExperimentalSetup` and `DropData`                                         |
| **Fitting Dispatcher** | `modules/fitting/fits.py`   | Routes to various fitting methods (Polynomial, Circle, Ellipse, Young-Laplace, ML) |
| **Algorithms**         | `modules/fitting/BA_fit.py` | Individual fitting algorithm implementations                                       |

#### Analysis Pipelines

-   **Contact Angle**: `modules/contact_angle/` handles CA-specific processing
-   **Interfacial Tension**: `modules/ift/` handles IFT-specific processing with C++/Cython extensions
-   **Machine Learning**: `modules/ML_model/` contains TensorFlow models for Conan-ML

#### Data Flow

```
Image Acquisition → Preprocessing → Contour Extraction → Fitting → Results
```

### 3.4. Frontend Architecture (`views/`)

#### Framework & Navigation

-   **Framework**: Built with **CustomTkinter** (themed extension of Tkinter)
-   **Navigation Controller**: `views/function_window.py` manages page transitions using `show_frame()`
-   **Page Structure**: All UI pages are subclasses of `CTkFrame`

#### Shared State Management

-   **Global State**: `user_input_data` object passed across all pages
-   **Contains**: Input paths, selected methods, parameters
-   **Instantiated in**: `function_window.py`

#### Workflow Pages

| Stage           | Contact Angle       | Interfacial Tension  |
| --------------- | ------------------- | -------------------- |
| **Acquisition** | `acquisition.py`    | `acquisition.py`     |
| **Preparation** | `ca_preparation.py` | `ift_preparation.py` |
| **Analysis**    | `ca_analysis.py`    | `ift_analysis.py`    |
| **Output**      | `output_page.py`    | `output_page.py`     |

#### Reusable Components

-   **Location**: `views/component/`
-   **Examples**: Custom entry fields, validation widgets, common UI patterns

## 4. Contribution Workflow

We use a **develop-centric branching model** for development and collaboration.

### 4.1. Branching Strategy

#### Main Branches

| Branch        | Purpose                                                                 | Access                    |
| ------------- | ----------------------------------------------------------------------- | ------------------------- |
| **`develop`** | Main integration branch for all development features and default branch | Direct commits ❌, PRs ✅ |
| **`main`**    | Stable, release-ready code                                              | Release Manager only      |

#### Development Branches

| Branch Type | Naming Convention                | Created From | Merged To          |
| ----------- | -------------------------------- | ------------ | ------------------ |
| **Feature** | `feature/short-descriptive-name` | `develop`    | `develop`          |
| **Release** | `release/version-number`         | `develop`    | `main` + `develop` |
| **Hotfix**  | `hotfix/issue-fix`               | `main`       | `main` + `develop` |

#### Feature Branch Workflow

1. **Create GitHub Issue** → Assign to yourself
2. **Create Branch** → Use "Create branch" button on GitHub issue
3. **Develop** → Make your changes
4. **Pull Request** → Merge back to `develop`

### 4.2. Pull Request (PR) Process

#### PR Requirements

-   [ ] Code follows project style guidelines
-   [ ] Clear PR description with linked GitHub issue(s)
-   [ ] All tests pass locally
-   [ ] At least one reviewer assigned
-   [ ] Review comments addressed

### 4.3. Code Review Guidelines

#### Review Focus Areas

-   **Correctness**: Logic and functionality
-   **Standards**: Adherence to coding guidelines
-   **Performance**: Efficiency considerations
-   **Maintainability**: Code clarity and documentation

#### Best Practices

-   Provide **constructive feedback**
-   Focus on **code, not the person**
-   Suggest **specific improvements**
-   Approve when standards are met

## 5. Coding Standards

Adherence to coding standards is crucial for maintaining **code quality** and **consistency**.

### 5.1. Python Style Guide

#### Core Standards

| Standard       | Tool     | Command                                       |
| -------------- | -------- | --------------------------------------------- |
| **PEP 8**      | Manual   | Follow [PEP 8](https://pep8.org/) style guide |
| **Formatting** | `black`  | `black .`                                     |
| **Linting**    | `flake8` | `flake8 .`                                    |

#### Documentation Requirements

-   **Docstrings**: Required for all modules, classes, functions, and methods
-   **Style**: Use [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) for docstrings
-   **Comments**: Explain complex or non-obvious code sections

#### Example Docstring

```python
def calculate_contact_angle(contour: np.ndarray) -> tuple[float, float]:
    """Calculate left and right contact angles from droplet contour.

    Args:
        contour: Droplet contour points as (N, 2) array of (x, y) coordinates.

    Returns:
        Tuple of (left_angle, right_angle) in degrees.

    Raises:
        ValueError: If contour has insufficient points for calculation.
    """
```

#### Linting Guide

Install pre commit linter to automatically lint (beautify) your files before every commit:

```
pre-commit install
```

The first time running may take a few minutes. Run manually:

```
pre-commit run --all-files
```

### 5.2. Commit Message Convention

#### Angular Convention Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

#### Commit Types

| Type       | Purpose            | Example                                               |
| ---------- | ------------------ | ----------------------------------------------------- |
| `feat`     | New feature        | `feat(fitting): add polynomial fit option for CA`     |
| `fix`      | Bug fix            | `fix(ui): resolve image scaling bug in analysis page` |
| `docs`     | Documentation      | `docs(readme): update installation instructions`      |
| `style`    | Formatting         | `style(views): apply black formatting`                |
| `refactor` | Code restructuring | `refactor(core): simplify data structures`            |
| `test`     | Testing            | `test(fitting): add unit tests for BA_fit`            |
| `chore`    | Maintenance        | `chore(deps): update requirements.txt`                |

#### Examples

```bash
feat(fitting): add polynomial fit option for CA
Closes #42

fix(ui): resolve image scaling bug in analysis page
Addresses #55, #57
```

### 5.3. Frontend Standards (CustomTkinter)

#### UI Guidelines

-   **Naming**: Use consistent naming conventions for UI elements
-   **Separation**: Keep UI logic separate from business logic
-   **Reusability**: Use shared components from `views/component/`
-   **Responsiveness**: Design for different screen sizes

#### Component Structure

```python
class MyCustomWidget(ctk.CTkFrame):
    """Custom widget with clear documentation."""

    def __init__(self, parent, user_input_data, **kwargs):
        super().__init__(parent, **kwargs)
        self.user_input_data = user_input_data
        self._setup_ui()

    def _setup_ui(self):
        """Initialize UI components."""
        # UI setup code here
```

## 6. Testing Procedures

Comprehensive testing ensures the **reliability** and **stability** of opendrop_ml. We use `pytest` as our testing framework.

> **Primary Reference**: See `TESTING.md` for complete testing instructions.

### 6.1. Testing Overview

#### Framework & Structure

| Aspect            | Details                               |
| ----------------- | ------------------------------------- |
| **Framework**     | `pytest`                              |
| **Test Location** | Co-located with modules (`*_test.py`) |
| **Entry Point**   | `test_all.py` for running all tests   |
| **Coverage**      | `modules/` and `views/` directories   |

#### Test File Examples

```
opendrop_ml/modules/fitting/
├── fits.py
├── fits_test.py
├── BA_fit.py
└── BA_fit_test.py

opendrop_ml/views/
├── acquisition.py
└── acquisition_test.py
```

> **Note**: There is **no separate `tests/` directory** - all tests are co-located with their source files.

### 6.2. Writing Tests

#### Test Types

| Type                  | Purpose                           | Guidelines                               |
| --------------------- | --------------------------------- | ---------------------------------------- |
| **Unit Tests**        | Test individual functions/methods | Use `pytest` fixtures, mock dependencies |
| **Integration Tests** | Test component interactions       | Focus on data flow between modules       |

#### Naming Conventions

-   **Files**: `test_*.py` or `*_test.py`
-   **Functions**: Prefix with `test_`

#### Example Test Structure

```python
import pytest
from modules.fitting.BA_fit import calculate_baseline_angle

class TestBaselineAngle:
    """Test cases for baseline angle calculation."""

    @pytest.fixture
    def sample_contour(self):
        """Provide sample contour data for testing."""
        return np.array([[10, 20], [15, 25], [20, 30]])

    def test_calculate_baseline_angle_valid_input(self, sample_contour):
        """Test baseline angle calculation with valid input."""
        result = calculate_baseline_angle(sample_contour)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_calculate_baseline_angle_empty_contour(self):
        """Test baseline angle calculation with empty contour."""
        with pytest.raises(ValueError):
            calculate_baseline_angle(np.array([]))
```

### 6.3. Running Tests

#### Basic Commands

| Command              | Purpose                             |
| -------------------- | ----------------------------------- |
| `python test_all.py` | Run all tests using unified script  |
| `pytest`             | Run all tests using pytest directly |
| `pytest -v`          | Run tests with verbose output       |

#### Specific Test Execution

```bash
# Run specific test file
pytest modules/fitting/fits_test.py

# Run specific test function
pytest modules/fitting/polynomial_fit_test.py::test_cluster_optics

# Run tests in specific directory
pytest modules/fitting/

# Run tests with pattern matching
pytest -k "test_baseline"
```

#### Test Coverage

```bash
# Generate coverage report
pytest --cov=modules --cov=views

# Generate HTML coverage report
pytest --cov=modules --cov=views --cov-report=html

# Coverage with missing lines
pytest --cov=modules --cov=views --cov-report=term-missing
```

### 6.4. Test Development Guidelines

#### Best Practices

-   **Focus**: Each test should verify one specific behavior
-   **Documentation**: Use descriptive test names and docstrings
-   **Fixtures**: Use pytest fixtures for test data setup
-   **Independence**: Tests should not depend on each other
-   **Mock External Dependencies**: Isolate units under test

#### Coverage Goals

-   **Target**: Aim for high test coverage (>80%)
-   **Priority**: Focus on critical paths and complex algorithms
-   **Documentation**: Include coverage reports in PRs

## 7. Deployment Guidelines

This section outlines the steps for **building**, **packaging**, and **deploying** the opendrop_ml project.

> **Note**: Information based on `setup.py` and Python best practices. May require expansion for specific deployment targets.

### 7.1. Building Cython Extensions

#### Prerequisites for C++ Modules

The project includes **performance-critical C++ modules** compiled with Cython, essential for IFT analysis.

| Dependency    | Purpose            | Platforms             |
| ------------- | ------------------ | --------------------- |
| **SUNDIALS**  | Numerical solving  | Windows, macOS, Linux |
| **Boost C++** | C++ libraries      | Windows, macOS, Linux |
| **Cython**    | Python-C++ binding | All platforms         |

#### Build Command

```bash
python setup.py build_ext --inplace
```

#### What This Does

-   Compiles `.pyx` files → C/C++ → Python extensions
-   Output: `.pyd` (Windows) or `.so` (Linux/macOS) files
-   Location: Placed in `modules/ift/younglaplace/` directory

> **Important**: Ensure C++ dependencies are correctly installed per `setup.py` configurations for your OS.

### 7.2. Core Packaging with `setup.py`

#### Setup.py Responsibilities

The `setup.py` script handles critical packaging tasks:

| Task                      | Description                                                           |
| ------------------------- | --------------------------------------------------------------------- |
| **Cython Compilation**    | Converts `.pyx` files to Python extensions                            |
| **Platform Dependencies** | Links OS-specific libraries (Windows `.lib`, Linux `.so`, macOS `.a`) |
| **Extension Definition**  | Configures source files, include dirs, compiler flags                 |
| **Integration**           | Places compiled modules in project structure                          |

#### Platform-Specific Libraries

```
dependencies/
├── windows/      # .lib files
├── macos_arm64/  # ARM64 .a/.so files
├── macos_x86_64/ # Intel .a/.so files
└── linux/        # .a/.so files
```

#### Compiler Configuration

-   **C++ Standard**: `-std=c++17`
-   **Include Paths**: Cython source, SUNDIALS, Boost headers
-   **Library Linking**: OS-specific static/dynamic libraries

### 7.3. Deployment Considerations

#### Cross-Platform Builds

| Platform    | Requirements              | Notes                      |
| ----------- | ------------------------- | -------------------------- |
| **Windows** | Visual Studio Build Tools | Use native Windows build   |
| **macOS**   | Xcode Command Line Tools  | Support both Intel & ARM64 |
| **Linux**   | GCC/Clang                 | Various distributions      |

> **Best Practice**: Build on each target OS for maximum compatibility.

#### Packaging Checklist

-   [ ] **Python Dependencies**: Bundle all `requirements.txt` packages
-   [ ] **C++ Extensions**: Include compiled `.pyx, .hpp, .pyd`/`.so` files from build step
-   [ ] **ML Models**: Include TensorFlow SavedModel from `modules/ML_model/`
-   [ ] **Assets**: Include fonts, images from `assets/` directory
-   [ ] **Configuration**: Include `user_config.yaml` defaults

#### Common Packaging Tools

| Tool            | Purpose                 | Use Case                     |
| --------------- | ----------------------- | ---------------------------- |
| **PyInstaller** | Standalone executables  | End-user distribution        |
| **cx_Freeze**   | Cross-platform freezing | Alternative to PyInstaller   |
| **Nuitka**      | Python compiler         | Performance-optimized builds |

#### Example PyInstaller Command

```bash
pyinstaller --onefile --windowed --add-data "assets;assets" --add-data "modules/ML_model;modules/ML_model" main.py
```

Eensure the `/` is the correct one for your platform. A platform independant pyinstaller command is used in `install.py` as part of the main.exe creation process in Windows.

### 7.4. Testing Packaged Applications

#### Validation Steps

1. **Clean Environment**: Test on systems without dev environment
2. **Dependency Check**: Verify all required libraries are bundled
3. **Path Verification**: Ensure relative paths work correctly
4. **ML Model Access**: Confirm TensorFlow models load properly
5. **C++ Extensions**: Test IFT analysis functionality

#### Platform Testing Matrix

| Platform      | Python | Architecture | Status   |
| ------------- | ------ | ------------ | -------- |
| Windows 10/11 | 3.8.10 | x64          | Required |
| macOS         | 3.8.10 | Intel x64    | Required |
| macOS         | 3.8.10 | ARM64        | Required |
| Ubuntu LTS    | 3.8.10 | x64          | Required |

## 8. Further Information

### 8.1. Configuration & Customization

| File                   | Purpose                      | Documentation                    |
| ---------------------- | ---------------------------- | -------------------------------- |
| **`user_config.yaml`** | Default application settings | Modify for custom configurations |
| **`requirements.txt`** | Python dependencies          | Update when adding new packages  |
| **`.python-version`**  | Python version specification | Maintain version consistency     |

### 8.2. Resources & Support

#### Documentation

-   **Main Guide**: This Developer Guide (comprehensive reference)
-   **User Guide**: `README.md` (end-user instructions)
-   **Testing**: `TESTING.md` (testing procedures)

#### Troubleshooting

1. **Check Logs**: Review application output for error messages
2. **GitHub Issues**: Search existing issues or create new ones
3. **Team Consultation**: Reach out to other team members
4. **Dependencies**: Verify all requirements are properly installed

#### Quick Navigation

-   [Setup Instructions](#2-setup-instructions) - Get started quickly
-   [Project Structure](#3-project-structure) - Understand the codebase
-   [Testing Procedures](#6-testing-procedures) - Run and write tests

---

This Developer Guide serves as your **primary reference** for contributing to opendrop_ml.

---
