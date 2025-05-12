# OpenDrop-ML 

OpenDrop-ML is an open-source, cross-platform tool for analyzing liquid droplets in surface science using contact angle and pendant drop methods. It integrates classical geometric fitting with machine learning models (via Conan-ML), providing flexible, automated, and high-throughput image processing for researchers, technicians, and developers.

Current ML implementation is optimized for high angle systems. For lower angle or extreme curvature drops, verification of results is strongly advised. See: https://doi.org/10.1021/acs.langmuir.4c01050

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
│   ├── ca_*.py, ift_*.py    # CA/IFT workflows (acquisition → preparation → analysis → output)
│   ├── component/           # Reusable UI widgets
│   └── function_window.py   # Navigation controller
├── utils/                   # Helper code (config, validation, image IO)
├── tests/                   # Unit and integration tests
├── test_all.py              # py file to run all the unit tests
└── training files/          # ML training scripts and data
```

------

# Quick Start Guide

This guide helps you install the necessary dependencies and run the application on your local machine.

---

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
Download and install [Python 3.8.10](https://www.python.org/downloads/release/python-3810/), which is the recommended version for this project. Choose the installer for your operating system.

> **Windows Users:** During installation, **check the box** that says: *“Add Python to PATH”* 
> 
>  If you forget, you may need to manually add it to your **environment variables** under "System Properties > Environment Variables > Path".

> **macOS/Linux Users:** Python 3 is usually preinstalled, but you can install it via a package manager if needed:
> 
> macOS: ```brew install python@3.8```
> 
> Ubuntu/Debian: ```sudo apt install python3.8 python3.8-venv```
> 
> Fedora: ```sudo dnf install python3.8```

---

## 2. Install C/C++ Build Tools

Cython and some Python packages require C/C++ compilers to build native extensions.

### Windows

- Download and install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- During installation, select:
  - "C++ build tools"
  - Include the "Windows 10 SDK" or "Windows 11 SDK"

### macOS
- Open Terminal and install Xcode Command Line Tools:
  ```bash
  xcode-select --install
  ```

### Linux
- For Debian/Ubuntu based systems:
  ```bash
  sudo apt update
  sudo apt install build-essential
  ```

- For Fedora/RHEL based systems:
  ```bash
  sudo dnf groupinstall "Development Tools"
  ```

- For Arch Linux:
  ```bash
  sudo pacman -S base-devel
  ```

---

## 3. Install Python Dependencies

Make sure you're in the root folder of the project, then run:

```bash
pip install -r requirements-3810.txt
```

This will install all necessary packages.

> If you’re using a virtual environment, activate it first:

On Windows
```bash
python -m venv venv
venv\Scripts\activate
```

On macOS or Linux
```bash
python -m venv venv
source venv/bin/activate
```

---

## 4. Build Cython Extensions

You’ll need to compile Cython modules before running the application:

```bash
python setup.py build_ext --inplace
```

This will generate`.cpp` files from the Cython sources.

> If you encounter errors, ensure:
> - Cython is installed: `pip install cython`
> - C/C++ Build Tools are properly installed (step 2)

---

## 5. Run the Application

Once the build is complete, run the main script to start the application:

```bash
python main.py
```

If your application has a GUI or a web interface, follow any additional prompts or check the console for access URLs.

---

## Troubleshooting

- **Python not recognized?**
  - Make sure it’s added to `PATH` in your environment variables.

- **Cython build errors?**
  - Confirm you installed the C++ Build Tools (step 2).
  - Try `pip install --upgrade pip setuptools wheel cython`.

- **Wrong Python version?**
  - Consider using `pyenv`, `conda`, or a virtual environment to manage Python versions.

# User Guide
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

# Contact & Contribution

OpenDrop-ML is an open-source project. Contributions are welcome!

- GitHub: https://github.com/SamSike/OpenDrop_OP
- For issues, use GitHub issue tracker

# Appropriate use

This section has been included as many users of Conan-ML will not be familiar
with the use of ML models and their limitations and best practice use cases.

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