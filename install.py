from utils.os import is_windows
import sys
import os
import shutil
import subprocess
import glob
import PyInstaller.__main__

"""
Usage:

    Install:        python install.py

    --no-msi:       Skip building the Windows installer (MSI)
    --test:         Test the built .exe file

    --no-pip:       Skip building the pip package
    --upload:       Upload to PyPI (if --no-pip is not set)


    By default, builds the Windows installer and pip package
    By default, does not upload to PyPI

    Building the Windows installer (heat, candle, light steps)
    requires WiX Toolset installed (only on Windows)
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


"""
    Get the version from the METADATA file.
    Can not be imported from setup.py
"""
with open(os.path.join(os.path.dirname(__file__), "METADATA"), "r") as metadata_file:
    metadata = metadata_file.read().strip().split("\n")
    PACKAGE_NAME = metadata[0].split(": ")[1].strip()
    VERSION = metadata[1].split(": ")[1].strip()

sep = ";" if is_windows() else ":"
pip_package_name = f"{PACKAGE_NAME}-{VERSION}.tar.gz"


if __name__ == "__main__":
    if "--no-msi" not in sys.argv or "--no-pip" not in sys.argv:
        # Remove build and dist directories
        remove_dir("dist")
        remove_dir("build")

    if "--no-msi" not in sys.argv:

        # Build Cython extensions
        run("python setup.py build_ext --inplace")

        # Remove .pyc files and __pycache__ folders
        remove_files(os.path.join("**", "*.pyc"))
        remove_pycache(".")

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
                f"assets{sep}assets",
                "--add-data",
                f"user_config.yaml{sep}.",
                "--add-data",
                f"{os.path.join('modules', 'ML_model')}{sep}{os.path.join('modules', 'ML_model')}",
                "--add-data",
                f"experimental_data_set{sep}experimental_data_set",
                "--add-data",
                f"training_files{sep}training_files",
                "--add-data",
                f"sensitivity_data_set{sep}sensitivity_data_set",
                # if fails due to missing files, can add them manually
                # '--add-binary', 'modules/ift/younglaplace/shape*.pyd;modules/ift/younglaplace',
                # add hidden imports that are not being collected automatically
                # and throw errors
                "--hidden-import",
                "PIL._tkinter_finder",
                # clean up previous builds
                "--clean",
                # output in one directory instead of one huge exe file
                "--onedir",
                "--icon",
                os.path.join(
                    "assets", "opendrop.ico" if is_windows() else "opendrop.png"
                ),
                # no console window
                "--windowed",
                # do not require answering 'yes/no' to create msi
                "--noconfirm",
            ]
        )

        if is_windows():
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

        # Remove previous builds
        remove_files(os.path.join("**", "*.cpp"))
        remove_files(os.path.join("modules", "**", "*.so"))
        for path in glob.glob("**/*.egg-info", recursive=True):
            remove_dir(path)

        # Build Cython extensions
        run("python setup.py build_ext --inplace")
        run("python setup.py sdist bdist_wheel")

    if "--test" in sys.argv:
        tested = 0

        # test the built executable
        print("Testing dist/main/main.exe, output will be saved to outputs/output.log")
        exe_path = os.path.join("dist", "main", "main.exe")
        log_path = os.path.join("outputs", "output.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        if not is_windows():
            # Remove .exe extension for non-Windows
            exe_path = exe_path[:-4]

        if not os.path.exists(exe_path):
            print(f"Executable {exe_path} does not exist. Skipping test.")
        else:
            result = subprocess.run(f"{exe_path} > {log_path} 2>&1", shell=True)
            if result.returncode != 0:
                print(
                    "main.exe exited with errors. Outputting last 20 lines of output.log:"
                )
                with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()
                    for line in lines[-20:]:
                        print(line.rstrip())
                sys.exit(0)
            else:
                print("main.exe ran successfully. See output.log for details.")
                tested += 1

        # test the built pip package
        print("Testing built pip package...")
        package_path = glob.glob(os.path.join("dist", pip_package_name))

        if not package_path:
            print(f"Package {pip_package_name} does not exist. Skipping test.")
        else:
            print(f"Found packages: {package_path}")
            run(f"pip install {package_path[0]}", shell=True)
            print(f"Installed package {pip_package_name} successfully.")
            # Optionally, you can run a test script to verify the installation
            # run("python -c 'import opendrop2'", shell=True)
            tested += 1

        if tested == 0:
            print("No tests were run. Please check the build process.")
            sys.exit(1)
        else:
            print(f"Total tests run: {tested}. All tests passed successfully.")
            sys.exit(0)

    if "--upload" in sys.argv:
        print("Uploading to PyPI...")
        run(f"twine upload {' '.join(package_path)}", shell=True)
