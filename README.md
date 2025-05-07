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


# Dependencies

`pip install -r requirements-3810.txt`

## System Requirements
Python: 3.8+

Minimum: 2 GB RAM, supports USB cameras

Recommended: 4 GB RAM, NVIDIA GPU for ML inference


# Code Structure Overview

```
/ (project root)
├── main.py                  # Application entry point
├── modules/                 # Core backend logic (fitting, processing, ML)
│   ├── fits.py              # Dispatcher for fitting methods
│   ├── BA_fit.py, ellipse_fit.py, etc.
│   └── ML_model/            # TensorFlow model, input-output conversion
├── views/                  # Frontend UI (CustomTkinter)
│   ├── ca_*.py, ift_*.py    # CA/IFT workflows (acquisition → output)
│   ├── component/           # Reusable UI widgets
│   └── function_window.py   # Navigation controller
├── utils/                  # Helper code (config, validation, image IO)
├── tests/                  # Unit and integration tests
└── training files/         # ML training scripts and data
```

------


# Quick Start
## 1. Install Requirements
Python 3.8+ is recommended

`pip install -r requirements.txt`

## 2. Run the Application
`python main.py`

## 3. Use the Interface
1.Select: Contact Angle or Interfacial Tension

2.Upload Image(s)

3.Choose Fitting Method(s)

4.Run → View Results → Export (CSV)



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
![High-Level Project Plan](./High-Level%20Project%20Diagram_v2.png)


# Contact & Contribution

OpenDrop-ML is an open-source project. Contributions are welcome!

- GitHub: https://github.com/SamSike/OpenDrop_OP
- For issues, use GitHub issue tracker
