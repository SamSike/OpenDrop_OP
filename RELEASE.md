# Guide to Create New Release

## Windows Release (msi)

### Pre Requisites

1. Install WiX Toolset [https://wixtoolset.org/releases/]

    (Optional: Install WiX Visual Studio Extension)

2. Ensure PATH (system environmental variables) contains WiX

3. Ensure pyinstaller is installed

    ```bash
    pip install pyinstaller
    ```

4. Update `windows-installer.wxs`:

    1. Create new GUID (using powershell)

        ```powershell
        [guid]::NewGuid()
        ```

    2. Update version number in Product tag

5. Create msi installer

    ```bash
    python install.py --no-pip
    ```

6. Add release to GitHub

    1. On the right side of the GitHub page, click "Create a new release"
    2. Label release with opendrop version
    3. Add msi to binaries

## Python Release (pip)

1. Ensure PyPI account

2. Install twine

    ```bash
    pip install twine
    ```

3. Create distributions

    ```bash
    python install.py --no-msi
    ```

4. Test

5. Upload

    ```bash
    python install.py --no-msi --upload
    ```
