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
     pyinstaller --onefile main.py

     heat dir modules -cg ModulesFiles -dr INSTALLDIR -gg -ag -g1 -sfrag -srd -var var.ProjectDir -out dist/modules-files.wxs -xi __pycache__ -xi *.pyc -xi .DS_Store
     heat dir utils -cg UtilsFiles -dr INSTALLDIR -gg -ag -g1 -sfrag -srd -var var.ProjectDir -out dist/utils-files.wxs -xi __pycache__ -xi *.pyc -xi .DS_Store
     heat dir views -cg ViewsFiles -dr INSTALLDIR -gg -ag -g1 -sfrag -srd -var var.ProjectDir -out dist/views-files.wxs -xi __pycache__ -xi *.pyc -xi .DS_Store

     candle -dProjectDir=. -o dist/ windows-installer.wxs dist/*.wxs

     light dist/*.wixobj -o dist/OpenDrop.msi
    ```

3. Ensure build files are not pushed to git
