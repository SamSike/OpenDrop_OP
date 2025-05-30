# Guide to Create New Release

## Pre Requisites

1. Install WiX Toolset [https://wixtoolset.org/releases/]

    (Optional: Install WiX Visual Studio Extension)

2. Ensure PATH (system environmental variables) contains WiX

3. Ensure pyinstaller is installed

    ```bash
    pip install pyinstaller
    ```

## Windows Release (msi)

1. Update `windows-installer.wxs`:

    1. Create new GUID (using powershell)

        ```powershell
        [guid]::NewGuid()
        ```

    2. Update version number in Product tag

2. Create msi installer

    ```bash
    python3 install.py
    ```

3. Ensure build files are not pushed to git
