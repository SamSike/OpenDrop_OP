import sys
import os
import shutil
import subprocess
import glob
import PyInstaller.__main__

"""
Usage:

    Install:        python install.py
    Upload to PyPI: python install.py --upload
    Test .exe:      python install.py --test

    Skip MSI:       python install.py --no-msi
    Skip pip:       python install.py --no-pip
"""


def remove_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"Removed directory: {path}")


def remove_files(pattern):
    for file in glob.glob(pattern, recursive=True):
        try:
            os.remove(file)
            print(f"Removed file: {file}")
        except Exception:
            pass


def remove_pycache(root="."):
    for dirpath, dirnames, _ in os.walk(root):
        for dirname in dirnames:
            if dirname == "__pycache__":
                full_path = os.path.join(dirpath, dirname)
                shutil.rmtree(full_path, ignore_errors=True)
                print(f"Removed __pycache__: {full_path}")


def run(cmd, shell=True):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=shell)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")


if __name__ == "__main__":
    # Remove build and dist directories
    remove_dir("dist")
    remove_dir("build")

    # Build Cython extensions
    run("python setup.py build_ext --inplace")

    # Remove .pyc files and __pycache__ folders
    remove_files("**/*.pyc")
    remove_pycache(".")

    if "--no-msi" not in sys.argv:
        # Build PyInstaller bundle
        PyInstaller.__main__.run(
            [
                "main.py",
                # add all root dir folders
                # (to exclude unrelated files such as dependencies/)
                "--collect-submodules",
                "modules",
                "--collect-submodules",
                "views",
                "--collect-submodules",
                "utils",
                # collect all non-python files
                "--add-data",
                "assets;assets",
                "--add-data",
                "user_config.yaml;.",
                "--add-data",
                "modules/ML_model;modules/ML_model",
                # if fails due to missing files, can add them manually
                # '--add-binary', 'modules/ift/younglaplace/shape*.pyd;modules/ift/younglaplace',
                # clean up previous builds
                "--clean",
                # output in one directory instead of one huge exe file
                "--onedir",
                "--icon",
                "assets/opendrop.ico",
                # no console window
                "--windowed",
                # do not require answering 'yes/no' to create msi
                "--noconfirm",
            ]
        )

        if "--test" in sys.argv:
            print(
                "Testing dist/main/main.exe, output will be saved to outputs/output.log"
            )
            result = subprocess.run(
                "dist\\main\\main.exe > outputs\\output.log 2>&1", shell=True
            )
            if result.returncode != 0:
                print(
                    "main.exe exited with errors. Outputting last 20 lines of output.log:"
                )
                with open("output.log", "r", encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()
                    for line in lines[-20:]:
                        print(line.rstrip())
                sys.exit(0)
            else:
                print("main.exe ran successfully. See output.log for details.")

        # WiX heat/candle/light steps
        run(
            "heat dir dist\\main -cg MainFiles -dr INSTALLFOLDER -gg -g1 -sfrag -srd -sreg -scom -var var.MainDir -out dist/main-files.wxs"
        )
        run(
            "candle -dMainDir=dist\main -o dist/ windows-installer.wxs dist/main-files.wxs"
        )
        run("light -sw1076 dist/*.wixobj -o dist/OpenDrop.msi")
        print(
            "Windows Installation complete. The OpenDrop msi is saved at dist/OpenDrop.msi."
        )

    if "--no-pip" not in sys.argv:

        # Build Cython extensions
        run("python setup.py build_ext --inplace")
        run("python setup.py sdist bdist_wheel")

        if "--upload" in sys.argv:
            print("Uploading to PyPI...")
            run("twine upload dist/opendrop2*.tar.gz")
