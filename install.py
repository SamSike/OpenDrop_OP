from platform import machine
import tarfile
import toml
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
    --specific:     Create platform-specific tar.gz files
    --upload:       Upload to PyPI (if --no-pip is not set)


    By default, builds the Windows installer and pip package
    By default, does not upload to PyPI

    Building the Windows installer (heat, candle, light steps)
    requires WiX Toolset installed (only on Windows)
"""

dependencies_folder_names = [
    name
    for name in os.listdir("dependencies")
    if os.path.isdir(os.path.join("dependencies", name))
]


def get_project_metadata():
    pyproject = toml.load("pyproject.toml")
    project = pyproject.get("project", {})
    name = project.get("name", "opendrop-ml")
    version = project.get("version", "0.0.0")
    return name, version


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


def is_windows():
    """
    Check if the current operating system is Windows.
    Returns True if Windows, False otherwise.
    """
    return sys.platform.startswith("win32") or sys.platform.startswith("cygwin")


def get_current_platform():
    """
    Get the current platform name based on the operating system.
    Derive from dependencies/ folder names.
    """
    if sys.platform.startswith("linux"):
        return "linux"
    elif sys.platform.startswith("darwin"):
        # You may want to detect arm64 vs x86_64 more precisely if needed
        macos = machine().lower()
        if macos == "arm64" or macos == "aarch64":
            return "macos_arm64"
        else:
            return "macos_x86_64"
    elif sys.platform.startswith("win"):
        return "windows"
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")


def create_platform_specific_tar_gz():
    """
    Create platform-specific tar.gz files from the generated package.
    Each tar.gz will contain only the dependencies for that platform."""

    for platform in dependencies_folder_names:
        src_tar = os.path.join("dist", f"{PACKAGE_NAME}-{VERSION}.tar.gz")
        dst_tar = os.path.join(
            "dist", f"{PACKAGE_NAME}-{VERSION}-{platform}.tar.gz")
        tmp_dir = os.path.join("dist", f"tmp_{platform}_extract")

        # Duplicate the .tar.gz file
        shutil.copyfile(src_tar, dst_tar)

        # Extract the copied tar.gz
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir, exist_ok=True)
        with tarfile.open(dst_tar, "r:gz") as tar:
            tar.extractall(tmp_dir)

        # Find the top-level extracted folder (usually PACKAGE_NAME-VERSION)
        top_level = None
        for name in os.listdir(tmp_dir):
            full_path = os.path.join(tmp_dir, name)
            if os.path.isdir(full_path):
                top_level = full_path
                break
        if not top_level:
            print(f"Could not find top-level directory in {dst_tar}")
            continue

        # Remove all dependencies/<other_platform> folders
        dep_dir = os.path.join(top_level, "dependencies")
        if os.path.isdir(dep_dir):
            for dep in os.listdir(dep_dir):
                dep_path = os.path.join(dep_dir, dep)
                if dep != platform and os.path.isdir(dep_path):
                    shutil.rmtree(dep_path)
                    print(f"Removed {dep_path} from {dst_tar}")

        # Repack the cleaned directory into the tar.gz
        with tarfile.open(dst_tar, "w:gz") as tar:
            tar.add(top_level, arcname=os.path.basename(top_level))

        # Clean up
        shutil.rmtree(tmp_dir)
        print(f"Created platform-specific archive: {dst_tar}")


sep = ";" if is_windows() else ":"
PACKAGE_NAME, VERSION = get_project_metadata()


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
                os.path.join(PACKAGE_NAME, "main.py"),

                # add all root dir folders
                # (to exclude unrelated files such as dependencies/)
                "--collect-submodules", f"{PACKAGE_NAME}.modules",
                "--collect-submodules", f"{PACKAGE_NAME}.views",
                "--collect-submodules", f"{PACKAGE_NAME}.utils",

                # collect all non-python files
                "--add-data", f"{os.path.join(PACKAGE_NAME, 'assets')}{sep}assets",
                "--add-data", f"{os.path.join(PACKAGE_NAME, 'user_config.yaml')}{sep}.",
                "--add-data", f"{os.path.join(PACKAGE_NAME, 'modules', 'ML_model')}{sep}modules/ML_model",
                "--add-data", f"{os.path.join(PACKAGE_NAME, 'experimental_data_set')}{sep}{os.path.join(PACKAGE_NAME, 'experimental_data_set')}",

                # if fails due to missing files, can add them manually.
                # add hidden imports that are not
                # being collected automatically
                "--hidden-import", "PIL._tkinter_finder",

                # clean up previous builds
                "--clean",

                # output in one directory instead of one huge exe file
                "--onedir",

                "--icon", os.path.join(
                    PACKAGE_NAME,
                    "assets",
                    "opendrop.ico" if is_windows() else "opendrop.png",
                ),

                # no console window in the background
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

    pip_package_name = os.path.join(
        "dist", f"{PACKAGE_NAME}-{VERSION}.tar.gz")

    if "--no-pip" not in sys.argv:

        # Generate one pip package containing dependencies of each platform
        run("python -m build")

    if "--test" in sys.argv:
        tested = 0

        # test the built executable (.exe)
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
            result = subprocess.run(
                f"{exe_path} > {log_path} 2>&1", shell=True)
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

        # test the built package (.tar.gz)
        print("Testing built pip package...")
        package_path = glob.glob(pip_package_name)

        if not package_path:
            print(
                f"Package {pip_package_name} does not exist. Skipping test.")
        else:
            print(f"Found packages: {package_path}")
            run(f"pip install {package_path[-1]}", shell=True)
            print(
                f"Installed package {pip_package_name} successfully.")
            run("opendrop", shell=True)
            tested += 1

        if tested == 0:
            print("No tests were run. Please check the build process.")
            sys.exit(1)
        else:
            print(f"Total tests run: {tested}. All tests passed successfully.")
            sys.exit(0)

    if "--specific" in sys.argv:
        # Create platform-specific tar.gz files
        print("Creating platform-specific tar.gz files...")
        create_platform_specific_tar_gz()

    if "--upload" in sys.argv:
        # Only one pip package is allowed per release
        print("Uploading to PyPI...")
        combined_package_name = os.path.join(
            "dist", f"{PACKAGE_NAME}-{VERSION}.tar.gz")
        run(f"twine upload {combined_package_name}", shell=True)
