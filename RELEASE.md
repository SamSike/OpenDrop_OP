# Guide to Create New Release

## Pre Requisites

1. Install WiX Toolset [https://wixtoolset.org/releases/]

    (Optional: Install WiX Visual Studio Extension)

2. Ensure pyinstaller is installed

    ```bash
    pip install pyinstaller
    ```

## Windows Release (msi)

```bash
pyinstaller --onefile main.py
```
