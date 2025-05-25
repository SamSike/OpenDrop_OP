# OpenDrop-ML

OpenDrop-ML is an open-source, cross-platform tool for analyzing liquid droplets in surface science using contact angle and pendant drop methods. It integrates classical geometric fitting with machine learning models (via Conan-ML), providing flexible, automated, and high-throughput image processing for researchers, technicians, and developers.

Current ML implementation is optimized for high angle systems. For lower angle or extreme curvature drops, verification of results is strongly advised. See: [https://doi.org/10.1021/acs.langmuir.4c01050](https://doi.org/10.1021/acs.langmuir.4c01050)

# Table of Contents

- [OpenDrop-ML](#opendrop-ml)
- [Table of Contents](#table-of-contents)
- [Features](#features)
- [Code Structure Overview](#code-structure-overview)
- [Quick Start Guide for Windows and Linux](#quick-start-guide-for-windows-and-linux)
  - [1. Install Python](#1-install-python)
    - [Check if Python is Already Installed](#check-if-python-is-already-installed)
    - [Install Python (if not already installed)](#install-python-if-not-already-installed)
  - [2. Install C/C++ Build Tools](#2-install-cc-build-tools)
  - [3. (Optional) Create and Use a Virtual Environment](#3-optional-create-and-use-a-virtual-environment)
  - [4. Install Python Dependencies](#4-install-python-dependencies)
  - [5. Build Cython Extensions](#5-build-cython-extensions)
  - [6. Run the Application](#6-run-the-application)
- [Quick Start Guide for macOS (Intel \& Apple Silicon)](#quick-start-guide-for-macos-intel--apple-silicon)
  - [1. Install Python](#1-install-python-1)
  - [2. Set Up Virtual Environment (Intel \& Apple Silicon)](#2-set-up-virtual-environment-intel--apple-silicon)
    - [Install Conda or Pyenv](#install-conda-or-pyenv)
    - [Create Python Environment](#create-python-environment)
    - [Install Python Dependencies](#install-python-dependencies)
  - [3. Build Cython Extensions](#3-build-cython-extensions)
  - [4. Run the Application](#4-run-the-application)
  - [Troubleshooting:](#troubleshooting)
    - [1. SUNDIALS:Architecture Mismatch (macOS)](#1-sundialsarchitecture-mismatch-macos)
    - [✅ Fix Steps](#-fix-steps)
    - [2. Boost: File not found](#2-boost-file-not-found)
    - [✅ Fix Steps](#-fix-steps-1)
    - [3. Check Build Library](#3-check-build-library)
    - [Boost](#boost)
    - [About SUNDIALS](#about-sundials)
    - [✅ You can skip this step if:](#-you-can-skip-this-step-if)
    - [⚠️ You must build manually with CMake if:](#️-you-must-build-manually-with-cmake-if)
- [User Configuration Guide](#user-configuration-guide)
  - [📁 File Structure Example](#-file-structure-example)
  - [✅ Allowed Values](#-allowed-values)
    - [Drop/Needle Region Methods](#dropneedle-region-methods)
    - [Threshold/Baseline Method](#thresholdbaseline-method)
    - [Edge Detection](#edge-detection)
    - [Image Source](#image-source)
  - [Tips](#tips)
- [Full Workflow](#full-workflow)
- [Developer \& Contributor Guide](#developer--contributor-guide)
  - [Modular Design](#modular-design)
  - [Backend \& UI Extensions](#backend--ui-extensions)
- [High-Level Architecture Diagram](#high-level-architecture-diagram)
- [Unit tests](#unit-tests)
- [Appropriate use of ML model in Contact Angle Analysis](#appropriate-use-of-ml-model-in-contact-angle-analysis)
- [Contact \& Contribution](#contact--contribution)

# Features

- Contact Angle & Pendant Drop Analysis
- Multiple Fitting Algorithms: Polynomial, circular, elliptical, Young-Laplace
- Integrated ML Prediction (Conan-ML) for contact angles
- High-throughput Batch Processing of images & videos
- Cross-platform Support: Windows, macOS, Linux
- User-friendly GUI built with CustomTkinter
- Modular Backend for easy customization and extension

# Code Structure Overview

```
/ (project root)
├── main.py                  # Application entry point
├── modules/                 # Core backend logic (fitting, processing, ML)
│   ├── fits.py              # Dispatcher for fitting methods
│   ├── BA_fit.py, ellipse_fit.py, etc.
│   └── ML_model/            # TensorFlow model, input-output conversion
├── views/                   # Frontend UI (CustomTkinter)
│   ├── ca_*.py, ift_*.py    # CA/IFT workflows
│   ├── component/           # Reusable UI widgets
│   └── function_window.py   # Navigation controller
├── utils/                   # Helper code (config, validation, image IO)
├── tests/                   # Unit and integration tests
├── test_all.py              # Run all tests
└── training files/          # ML training scripts and data
```

# Quick Start Guide for Windows and Linux

This guide helps you install the necessary dependencies and run OpenDrop-ML on your local Windows and Linux machine. MacOS users please refer to [Quick Start Guide for macOS (Conda Only)](#quick-start-guide-for-macos-conda-only).

## 1. Install Python

### Check if Python is Already Installed

Open a terminal (Command Prompt or PowerShell) and run:

```bash
python --version
```

or:

```bash
py --version
```

If Python is installed, it will show the version.

### Install Python (if not already installed)

Download and install [Python 3.8.10](https://www.python.org/downloads/release/python-3810/), which is the recommended version for this application. Choose the installer for your operating system.

> **Windows Users:** During installation, **check the box** that says: _“Add Python to PATH”_
>
> If you forget, you may need to manually add it to your **environment variables** under "System Properties > Environment Variables > Path".

> **Linux Users:** Python 3 is usually preinstalled, but you can install it via a package manager if needed:
>
> Ubuntu/Debian: `sudo apt install python3.8 python3.8-venv`
>
> Fedora: `sudo dnf install python3.8`

## 2. Install C/C++ Build Tools

- **Windows**:
  - Download and install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
  - During installation, select:
    - "C++ build tools"
    - Include the "Windows 10 SDK" or "Windows 11 SDK"
- **Linux**:

```bash
sudo apt install build-essential   # Debian/Ubuntu
sudo dnf groupinstall "Development Tools"  # Fedora
```

## 3. (Optional) Create and Use a Virtual Environment

It is recommended (but not required) to use a Python virtual environment to isolate dependencies.

To create and activate a virtual environment:

```bash
# Create the virtual environment (only needed once)
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Linux:
source venv/bin/activate
```

Once activated, your shell should show `(venv)` at the beginning of the prompt.

> ⚠️ **Note**: If you choose to use the virtual environment, make sure to activate it every time you want to run the application.

To deactivate the environment at any time:

```bash
deactivate
```

You can skip these steps if you prefer to install packages globally (not recommended for development environments since there might be conflicts with existing Python setups or system packages).

## 4. Install Python Dependencies

Make sure you're in the root folder of the application, then run:

```bash
pip install -r requirements.txt
```

(Do this **after activating** the virtual environment, if you're using one.)

## 5. Build Cython Extensions

```bash
python setup.py build_ext --inplace
```

## 6. Run the Application

```bash
python main.py
```

# Quick Start Guide for macOS (Intel & Apple Silicon)

## 1. Install Python

Check if Python is installed:

```bash
python --version
```

If not, install [Python 3.8.10](https://www.python.org/downloads/release/python-3810/).

## 2. Set Up Virtual Environment (Intel & Apple Silicon)

### Install Conda or Pyenv

- **Apple Silicon**: Install [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install)
- **Intel Mac**: Conda optional — can use system Python or [pyenv](https://github.com/pyenv/pyenv)

### Create Python Environment

**Apple Silicon (Must use Conda)**

```bash
conda create -n opendrop_env -c conda-forge python=3.8.10
conda activate opendrop_env
```

**Intel Mac (Prefer Python, Conda optional)**

```bash
python3 -m venv opendrop_env # Skip this line if you want to install the required packages globally
source opendrop_env/bin/activate # Skip this line if you want to install the required packages globally
```

### Install Python Dependencies

Make sure you're in the root folder of the application, then run:

```bash
pip install -r requirements.txt
```

> ⚠️ **Note**: If you choose to use the virtual environment, make sure to activate it every time you want to run the application. If it is activate, `(venv)` will show at the beginning of the prompt.

To deactivate the environment at any time:

```bash
deactivate
```

## 3. Build Cython Extensions

```bash
python setup.py build_ext --inplace
```

## 4. Run the Application

```bash
python main.py
```

## Troubleshooting:

### 1. SUNDIALS:Architecture Mismatch (macOS)

If you see:

```
ImportError: ... incompatible architecture (have 'arm64', need 'x86_64h' or 'x86_64')
```

or:

```
ImportError: ... incompatible architecture (have 'x86_64', need 'arm64e' or 'arm64')
```

This means `.so` files were built under the wrong architecture.

### ✅ Fix Steps

```bash
python setup.py clean --all
rm -rf build modules/ift/**/**/*.so
python setup.py build_ext --inplace
python main.py
```

💡 **Tip**: Always recompile if switching between Intel and Apple Silicon.

### 2. Boost: File not found

If you see:

```
fatal error: 'boost/math/differentiation/autodiff.hpp' file not found
#include <boost/math/differentiation/autodiff.hpp>
```

### ✅ Fix Steps

1. Use Pre-included Dependencies (Preferred)

This project already includes a dependencies/ folder containing Boost and Sundials.
Make sure your build system or environment points to those directories.

You can resolve this issue by locating all .hpp files present in your Boost directory and ensuring that the path to Boost headers is correctly specified.

2. Locate Boost Header Files (If using system-installed Boost)

- Use the following command to find all .hpp files within the Boost directory:

```bash
find /opt/homebrew -name  "*.hpp" | grep boost # Apple Silicon
find /usr/local -name "*.hpp" | grep boost #Apple Intel
```

- Set the BOOST_INCLUDE_DIR Environment Variable

- Once you have identified the correct path to the Boost headers, set the BOOST_INCLUDE_DIR environment variable to this path.

```bash
export BOOST_INCLUDE_DIR=/opt/homebrew/Cellar/boost/1.88.0/include/ # Apple Silicon
#or
export CPLUS_INCLUDE_PATH=/opt/homebrew/include:$CPLUS_INCLUDE_PATH


export BOOST_INCLUDE_DIR=/usr/local/Cellar/boost/1.88.0/include/ #Apple Intel
#or
export CPLUS_INCLUDE_PATH=/usr/local/include:$CPLUS_INCLUDE_PATH

⚙️ Rebuild After Setting Path
python setup.py build_ext --inplace
python main.py
```

### 3. Check Build Library

### Boost

To check if Boost is installed on your system and available for your build, here’s how you can do it per platform:

Apple Silicon

```bash
find /usr /opt /homebrew/local -name version.hpp | grep boost
```

Apple Intel

```bash
find /usr /opt /usr/local -name version.hpp | grep boost
```

If it returns a path like /opt/homebrew/include/boost/version.hpp or /usr/local/include/boost/version.hpp, then Boost is installed.

otherwise

```bash
brew install boost
```

### About SUNDIALS

If you are on macOS, SUNDIALS static libraries must be available in:

dependencies/macos_x86_64/sundials/lib/ # for Intel Mac  
dependencies/macos_arm64/sundials/lib/ # for Apple Silicon (M1/M2/M3)

They're on a different architecture (e.g., you're Intel, they're Apple Silicon),
Or if .a files are missing or broken,
Then they must recompile using CMake.

### ✅ You can skip this step if:

The correct .a static libraries already exist for your architecture
Files like the following are present:
libsundials_arkode.a
libsundials_nvecserial.a
libsundials_core.a

### ⚠️ You must build manually with CMake if:

You're on a different architecture than the one the libraries were built for
The .a files are missing or broken

```bash
cd dependencies/macos_x86_64   # or macos_arm64

rm -rf sundials   # delete existing repo if present

git clone https://github.com/LLNL/sundials.git
cd sundials
mkdir build && cd build

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_STATIC_LIBS=ON \
  -DBUILD_SHARED_LIBS=OFF \
  -DSUNDIALS_BUILD_EXAMPLES=OFF \
  -DCMAKE_INSTALL_PREFIX=../../sundials

make -j4
make install
```

Ensure `.a` files are built in:

- `macos_x86_64/sundials/lib/`
- or `macos_arm64/sundials/lib/`

If you encounter errors, verify:

- Python version
- Cython is installed: `pip install cython`
- C++ compiler is correctly installed

# User Configuration Guide

[user_config.yaml](./user_config.yaml) is a YAML-based configuration file that lets you **predefine all key parameters** for your experiment, including:

- Image processing methods
- Physical properties
- Visualization flags
- File paths and outputs

You can avoid setting parameters manually in code — just edit the YAML file.

---

## 📁 File Structure Example

```yaml
# --- Image capture settings ---
drop_ID_method: Automated
threshold_method: Automated
needle_region_method: Automated
threshold_val: null
baseline_method: Automated
edgefinder: OpenCV

# --- Physical properties input by user ---
drop_density: 1000
density_outer: 0
needle_diameter_mm: 0.7176
pixel_mm: null

# --- Processing control flags ---
original_boole: 0
cropped_boole: 0
threshold_boole: 0
image_source: Local images

# --- File and region definitions ---
import_files: null
frame_interval: 1

# --- Analysis methods ---
analysis_methods_ca:
  TANGENT_FIT: true
  POLYNOMIAL_FIT: true
  CIRCLE_FIT: false
  ELLIPSE_FIT: false
  YL_FIT: false
  ML_MODEL: false

analysis_methods_pd:
  INTERFACIAL_TENSION: true

# --- Output ---
save_images_boole: false
create_folder_boole: false
filename: result
output_directory: ./outputs/
```

---

## ✅ Allowed Values

### Drop/Needle Region Methods

- `Automated` (default)
- `User-selected`

### Threshold/Baseline Method

- `Automated` (default)
- `User-selected`

### Edge Detection

- `OpenCV`
- `Subpixel`
- `Both`

### Image Source

- `Local images`

---

## Tips

- `null` in YAML means the value is left unset (equivalent to `None` in Python).
- Boolean flags must be `true` / `false` (lowercase YAML syntax).
- Be sure to match key names and nesting exactly as shown above.

# Full Workflow

1. Select function: Contact Angle or Interfacial Tension
2. Upload image(s)
3. Fill in user input
4. View results
5. Save results to CSV (optional)

After starting the application:

1. Select one of the functions: Contact Angle or Interfacial Tension

![Main Menu](./assets/main_menu.png)

2. Upload Image(s)

![Aquisition_1](./assets/ca_aquisition_1.png)
![Aquisition_2](./assets/ca_aquisition_2.png)

3. Fill in user input. Note that the sample image is for contact angle, but the process is similar for interfacial tension.

![Preparation](./assets/ca_preparation.png)

4. Click 'next' to view the result!

![Analysis](./assets/ca_analysis.png)

5. Optionally save the result to a CSV file.

![Output](./assets/output.png)

# Developer & Contributor Guide

## Linting

Install pre commit linter to automatically lint (beautify) your files before every commit:

```
pre-commit install
```

The first time running may take a few minutes. Run manually:

```
pre-commit run --all-files
```

## Modular Design

OpenDrop-ML emphasizes extensibility:

Add a new fitting method: See modules/fits.py

Add a UI component: See views/component/

Add a page: Update views/function_window.py

## Backend & UI Extensions

Refer to:

“Add Backend Module Steps – Guide to adding new models”

“Add Frontend Module Steps – UI integration tutorial”

# High-Level Architecture Diagram

![High-Level Project Plan](./assets/high-level-project-diagram.png)

# Unit tests

See [TESTING.md](./TESTING.md) for more details on how to run the built-in unit tests.

# Appropriate use of ML model in Contact Angle Analysis

The key limitation of ML models is that accuracy may deteriorate when used
on systems which was not represented within it's training data. While it has
been shown that the model can be applied to systems of contact angles below
110°, caution should be applied applied in these cases. It is recommended that
contact angles are plotted and briefly examined (i.e. sense-checked) as
general practice, but particularly for systems outside of training domain.
Similarly, drops with Bond numbers greater than 2 were not included in the
training set and should be approached with caution.

Surface roughness and reflection were included to train the model to ignore
inputted data which is not the drop edge. However, few images with surface
roughness which deviated from the training data were included in the
experimental data set. As such users are again advised to check outputs
for systems outside of the training range.

As the resolution of an image can be altered, should the resolution of an
image be too high it will be lowered to give an input suitable for the
ML model. This is the only exception to the above limitations.

High quality edge detection should be used to achieve the best results.
This work presents an automated process, which still requires improvement,
but will likely be suitable for high contrast images. Users are recommended
to check that the detected edge is reasonable prior to accepting the results
outputted by any fitting or angle prediction approach.

Current OpenDrop-ML implementation performs best for contact angles above 110°. For low-angle or high-curvature drops, verification is advised. See: [https://doi.org/10.1021/acs.langmuir.4c01050](https://doi.org/10.1021/acs.langmuir.4c01050)

Users should validate predictions manually in cases:

- With extreme Bond numbers (>2)
- With strong surface roughness/reflections
- Outside of the model's trained contact angle range

# Contact & Contribution

OpenDrop-ML is an open-source project. Contributions are welcome!

- GitHub: https://github.com/SamSike/OpenDrop_OP
- For issues, use GitHub issue tracker
