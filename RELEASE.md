# Guide to Create New Release

Install dependencies for install.py

```bash
pip install -r requirements.txt
pip install pyinstaller toml twine build tarfile
```

## Windows Release (msi)

### Pre Requisites

1. Install WiX Toolset [https://wixtoolset.org/releases/]

   (Optional: Install WiX Visual Studio Extension)

2. Ensure PATH (system environmental variables) contains WiX

3. Update `windows-installer.wxs`:

   1. Create new GUID (using powershell)

      ```powershell
      [guid]::NewGuid()
      ```

   2. Update version number in Product tag

4. Create msi installer

   ```bash
   python install.py --no-pip
   ```

5. Add release to GitHub (after testing)

   1. On the right side of the GitHub page, click "Create a new release"
   2. Label release with opendrop version
   3. Add msi to binaries

## Python Release (pip)

1. Ensure PyPI account and get API token [https://pypi.org/manage/account/token/]

2. Create distributions

   ```bash
   python install.py --no-msi
   ```

3. Upload (after testing)

   ```bash
   python install.py --no-msi --no-pip --upload
   ```
