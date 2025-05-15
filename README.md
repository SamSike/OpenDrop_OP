# OpenDrop-ML

OpenDrop-ML is an open-source, cross-platform tool for analyzing liquid droplets in surface science using contact angle and pendant drop methods. It integrates classical geometric fitting with machine learning models (via Conan-ML), providing flexible, automated, and high-throughput image processing for researchers, technicians, and developers.

Current ML implementation is optimized for high angle systems. For lower angle or extreme curvature drops, verification of results is strongly advised. See: [https://doi.org/10.1021/acs.langmuir.4c01050](https://doi.org/10.1021/acs.langmuir.4c01050)

# Table of Contents

* [OpenDrop-ML](#opendrop-ml)
* [Table of Contents](#table-of-contents)
* [Features](#features)
* [Code Structure Overview](#code-structure-overview)
* [Quick Start Guide for Windows and Linux](#quick-start-guide-for-windows-and-linux)
* [Quick Start Guide for macOS (Intel & Apple Silicon)](#quick-start-guide-for-macos-intel--apple-silicon)
* [User Guide](#user-guide)
* [Developer & Contributor Guide](#developer--contributor-guide)
* [High-Level Architecture Diagram](#high-level-architecture-diagram)
* [Unit tests](#unit-tests)
* [Appropriate use of ML model in Contact Angle Analysis](#appropriate-use-of-ml-model-in-contact-angle-analysis)
* [Contact & Contribution](#contact--contribution)


# Features

* Contact Angle & Pendant Drop Analysis
* Multiple Fitting Algorithms: Polynomial, circular, elliptical, Young-Laplace
* Integrated ML Prediction (Conan-ML) for contact angles
* High-throughput Batch Processing of images & videos
* Cross-platform Support: Windows, macOS, Linux
* User-friendly GUI built with CustomTkinter
* Modular Backend for easy customization and extension

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

## 1. Install Python

Check if Python is installed:

```bash
python --version
```

If not, download and install [Python 3.8.10](https://www.python.org/downloads/release/python-3810/).

## 2. Install C/C++ Build Tools

* **Windows**: Install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) with Windows 10/11 SDK.
* **Linux**:

```bash
sudo apt install build-essential   # Debian/Ubuntu
sudo dnf groupinstall "Development Tools"  # Fedora
```

## 3. Install Python Dependencies

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements-3810.txt
```

## 4. Build Cython Extensions

```bash
python setup.py build_ext --inplace
```

## 5. Run the Application

```bash
python main.py
```


# Quick Start Guide for MacOS

## 1. Install Python

Check if Python is installed:

```bash
python --version
```

If not, download and install [Python 3.8.10](https://www.python.org/downloads/release/python-3810/).

## 2. Install Python Dependencies

### Intel Users


```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements-3810.txt
```
# Quick Start Guide for macOS (Intel & Apple Silicon)

## 1. Install Conda or Python

* Apple Silicon: Install [Miniforge](https://github.com/conda-forge/miniforge)
* Intel Mac: Conda optional. You can also use system Python or pyenv.

## 2. Create Environment

### Apple Silicon (Must use Conda)

```bash
CONDA_SUBDIR conda create -n opendrop_env python=3.8.10 numpy=1.22.4 scipy=1.7.3 pip -c conda-forge
conda activate opendrop_env
pip install tensorflow-macos==2.13.0
pip install -r requirements-3810-macos.txt
```

### Intel Mac (Python prefer,Conda optional)

```bash
python3 -m venv opendrop_env
source opendrop_env/bin/activate
pip install -r requirements-3810.txt
```
## 3. Build Sundials Library (macOS only)


For macOS users (Intel and Apple Silicon), manually build SUNDIALS:

```bash
cd dependencies/macos_x86_64   # or macos_arm64

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

Ensure the static `.a` files exist in `dependencies/macos_x86_64/sundials/lib/` or `macos_arm64/sundials/lib/`.

## 4. Build Cython Extensions

```bash
python setup.py build_ext --inplace
```

## 5. Run the Application

```bash
python main.py
```



## Troubleshooting

If you encounter errors, verify:

* Python version
* Cython is installed: `pip install cython`
* C++ compiler is correctly installed


# User Guide

1. Select function: Contact Angle or Interfacial Tension
2. Upload image(s)
3. Fill in user input
4. View results
5. Save results to CSV (optional)

# Developer & Contributor Guide

* Add fitting method: `modules/fits.py`
* Add UI component: `views/component/`
* Add navigation page: `views/function_window.py`

# High-Level Architecture Diagram

![High-Level Project Plan](./assets/high-level-project-diagram.png)

# Unit tests

Run all tests:

```bash
python test_all.py
```

# Appropriate use of ML model in Contact Angle Analysis

ML predictions should be verified in cases involving:

* Contact angles <110°
* Bond numbers >2
* Strong reflection/surface roughness

Current model performs best on high angle droplets. Use caution outside training domain.

# Contact & Contribution

* GitHub: [https://github.com/SamSike/OpenDrop\_OP](https://github.com/SamSike/OpenDrop_OP)
* Use GitHub Issues for bug reports, suggestions, or contributions.

---

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
* With extreme Bond numbers (>2)
* With strong surface roughness/reflections
* Outside of the model's trained contact angle range

# Contact & Contribution

OpenDrop-ML is an open-source project. Contributions are welcome!

- GitHub: https://github.com/SamSike/OpenDrop_OP
- For issues, use GitHub issue tracker