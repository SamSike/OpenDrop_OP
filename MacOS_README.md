# OpenDrop-ML (macOS Conda Version Only)

OpenDrop-ML is an open-source tool for analyzing liquid droplets using contact angle and pendant drop methods. It combines classical geometric fitting with machine learning models (via Conan-ML) to support automated and high-throughput image processing for surface science applications.

**Note**: This setup guide is tailored specifically for macOS users using Conda.

## Features

* Contact angle and pendant drop analysis
* Multiple fitting algorithms: polynomial, circular, elliptical, Young-Laplace
* Integrated ML prediction (Conan-ML)
* High-throughput batch processing of images/videos
* GUI built with CustomTkinter
* Modular backend for easy customization

## Code Structure

```
/ (project root)
├── main.py                  # Application entry point
├── modules/                 # Core logic: fitting, ML, image processing
│   └── ML_model/           # TensorFlow model and converters
├── views/                   # UI logic (CustomTkinter)
│   └── component/          # UI widgets
├── utils/                   # Helper functions and configs
├── tests/                   # Unit and integration tests
├── test_all.py              # Test runner
└── training files/          # ML training assets
```

---

## Quick Start for macOS (Conda Only)

### 1. Install Conda

We recommend [Miniforge (Apple Silicon)](https://github.com/conda-forge/miniforge) or [Miniconda (Intel)](https://docs.conda.io/en/latest/miniconda.html).

### 2. Create Conda Environment

#### For Apple Silicon (M1/M2/M3):

```bash
CONDA_SUBDIR=osx-64 conda create -n opendrop_env python=3.8.10 numpy=1.22.4 scipy=1.7.3 pip -c conda-forge
conda activate opendrop_env
pip install tensorflow-macos
```

#### For Intel Mac:

```bash
conda create -n opendrop_env python=3.8.10 numpy=1.22.4 scipy=1.7.3 pip -c conda-forge
conda activate opendrop_env
pip install tensorflow==2.13.0
```

### 3. Install Other Python Dependencies

```bash
pip install -r requirements-3810.txt
```

### 4. Build Cython Extensions (Optional)

```bash
python setup.py build_ext --inplace
```

### 5. Run the Application

```bash
python main.py
```

### 6. VS Code or Other IDE Setup (Optional but Recommended)

If you are using VS Code or another IDE:

1. Open the Command Palette (`⇧⌘P` or `Ctrl+Shift+P`)
2. Run `Python: Select Interpreter`
3. Choose the one showing your Conda environment, such as:

   ```
   Python 3.8.10 ('opendrop_env': conda)
   ```

This ensures VS Code uses the correct environment with the right versions of `numpy`, `scipy`, `tensorflow`, etc.

---

## Appropriate Use of ML Model

Current Conan-ML implementation performs best for contact angles above 110°. For low-angle or high-curvature drops, verification is advised. See: [https://doi.org/10.1021/acs.langmuir.4c01050](https://doi.org/10.1021/acs.langmuir.4c01050)

Users should validate predictions manually in cases:

* With extreme Bond numbers (>2)
* With strong surface roughness/reflections
* Outside of the model's trained contact angle range

High-contrast and well-segmented edge detection images yield the best results.

---

## Contact & Contribution

* GitHub: [https://github.com/SamSike/OpenDrop\_OP](https://github.com/SamSike/OpenDrop_OP)
* Issues: Please file on GitHub

Pull requests are welcome to extend fitting algorithms, UI modules, or training pipeline.

---

## Developer Notes

* Add fitting method: `modules/fits.py`
* Add frontend: `views/component/`
* Route logic: `views/function_window.py`

For more details, see `TESTING.md` and internal module documentation.

---

## Visual Workflow

1. Choose analysis mode (CA/IFT)
2. Upload images
3. Configure analysis parameters
4. View results, export to CSV

---

## License

OpenDrop-ML is distributed under MIT License.
