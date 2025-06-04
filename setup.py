from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import glob
import os
import sys
import platform

"""
Usage:
        python setup.py build_ext --inplace
        OPENDROP_SUPPRESS_WARNINGS=1 python setup.py build_ext --inplace
"""

# setup for hpp/cpp

# Module paths
BASE_DIR = "opendrop-ml"
IFT_DIR = os.path.join(BASE_DIR, "modules", "ift")
YOUNGLAPLACE_DIR = os.path.join(IFT_DIR, "younglaplace")
INCLUDE_DIR = os.path.join(IFT_DIR, "include")

# Dependencies paths
SUNDIALS_INCLUDE = os.path.join(
    "dependencies", "windows", "sundials", "include")
SUNDIALS_LIB = os.path.join("dependencies", "windows", "sundials", "lib")
BOOST_INCLUDE = os.path.join("dependencies", "windows", "boost")


# Compiler settings
is_windows = sys.platform.startswith("win")
is_linux = sys.platform.startswith("linux")

# macos - intel & silicon
is_macos = sys.platform == "darwin"
arch = platform.machine()

extra_objects = []
compile_args = []

if is_windows:
    SUNDIALS_INCLUDE = os.path.join(
        "dependencies", "windows", "sundials", "include")
    SUNDIALS_LIB = os.path.join("dependencies", "windows", "sundials", "lib")
    BOOST_INCLUDE = os.path.join("dependencies", "windows", "boost")
    extra_objects = [
        os.path.join(SUNDIALS_LIB, "sundials_arkode_static.lib"),
        os.path.join(SUNDIALS_LIB, "sundials_nvecserial_static.lib"),
        os.path.join(SUNDIALS_LIB, "sundials_core_static.lib"),
    ]
    compile_args.append("/std:c++17")
    print("Windows detected, using Windows-specific settings.")
    print(f"SUNDIALS_INCLUDE: {SUNDIALS_INCLUDE}")
    print(f"SUNDIALS_LIB: {SUNDIALS_LIB}")
    print(f"BOOST_INCLUDE: {BOOST_INCLUDE}")
    print(f"extra_objects: {extra_objects}")
    print(f"compile_args: {compile_args}")
elif is_macos:
    if arch == "arm64":
        platform_dir = "macos_arm64"
        print("macOS ARM64 detected.")
    else:
        platform_dir = "macos_x86_64"
        print("macOS Intel detected.")
    SUNDIALS_INCLUDE = os.path.join(
        "dependencies", platform_dir, "sundials", "include")
    SUNDIALS_LIB = os.path.join(
        "dependencies", platform_dir, "sundials", "lib")
    BOOST_INCLUDE = os.path.join("dependencies", platform_dir, "boost")
    extra_objects = [
        os.path.join(SUNDIALS_LIB, "libsundials_arkode.a"),
        os.path.join(SUNDIALS_LIB, "libsundials_nvecserial.a"),
        os.path.join(SUNDIALS_LIB, "libsundials_core.a"),
        os.path.join(SUNDIALS_LIB, "libsundials_sunmatrixdense.a"),
        os.path.join(SUNDIALS_LIB, "libsundials_sunlinsoldense.a"),
        os.path.join(SUNDIALS_LIB, "libsundials_sunnonlinsolnewton.a"),
    ]
    compile_args.append("-std=c++17")
    print("macOS detected, using macOS-specific settings.")
    print(f"SUNDIALS_INCLUDE: {SUNDIALS_INCLUDE}")
    print(f"SUNDIALS_LIB: {SUNDIALS_LIB}")
    print(f"BOOST_INCLUDE: {BOOST_INCLUDE}")
    print(f"extra_objects: {extra_objects}")
    print(f"compile_args: {compile_args}")
else:
    SUNDIALS_INCLUDE = os.path.join(
        "dependencies", "linux", "sundials", "include")
    SUNDIALS_LIB = os.path.join("dependencies", "linux", "sundials", "lib")
    BOOST_INCLUDE = os.path.join("dependencies", "linux", "boost")

    extra_objects = [
        os.path.abspath(os.path.join(SUNDIALS_LIB, "libsundials_arkode.a")),
        os.path.abspath(os.path.join(
            SUNDIALS_LIB, "libsundials_nvecserial.a")),
        os.path.abspath(os.path.join(SUNDIALS_LIB, "libsundials_core.a")),
    ]
    compile_args.append("-std=c++17")
    print("Linux detected, using Linux-specific settings.")
    print(f"SUNDIALS_INCLUDE: {SUNDIALS_INCLUDE}")
    print(f"SUNDIALS_LIB: {SUNDIALS_LIB}")
    print(f"BOOST_INCLUDE: {BOOST_INCLUDE}")
    print(f"extra_objects: {extra_objects}")
    print(f"compile_args: {compile_args}")

# Suppress warnings if the environment variable is set
if os.environ.get("OPENDROP_SUPPRESS_WARNINGS") == "1":
    if is_windows:
        compile_args.append("/wd4996")
    else:
        compile_args.append("-Wno-deprecated-declarations")
        compile_args.append("-Wno-sign-compare")
        compile_args.append("-Wno-unused-variable")

# Cython extension definitions
ext_modules = [
    Extension(
        name="opendrop-ml.modules.ift.younglaplace.shape",
        sources=[os.path.join(YOUNGLAPLACE_DIR, "shape.pyx")],
        language="c++",
        include_dirs=[YOUNGLAPLACE_DIR, INCLUDE_DIR,
                      SUNDIALS_INCLUDE, BOOST_INCLUDE],
        extra_objects=extra_objects,
        extra_compile_args=compile_args,
        define_macros=[("SUNDIALS_STATIC", 1)],
    ),
    Extension(
        name="opendrop-ml.modules.ift.hough.hough",
        sources=[os.path.join(IFT_DIR, "hough", "hough.pyx")],
        language="c++",
        include_dirs=[os.path.join(IFT_DIR, "hough")],
        extra_compile_args=compile_args,
    ),
]


def all_files_recursive(directory):
    return [
        f
        for f in glob.glob(os.path.join(directory, "**"), recursive=True)
        if os.path.isfile(f)
    ]


setup(
    name="opendrop-ml",
    version="4.0.0",
    packages=find_packages(),
    ext_modules=cythonize(
        ext_modules,
        compiler_directives={"language_level": "3"},
        include_path=["opendrop"],
    ),
    # non python files that need to be compiled
    package_data={
        "opendrop-ml": [
            "user_config.yaml",
            os.path.join("modules", "ift", "younglaplace", "shape.pyx"),
            os.path.join("modules", "ift", "hough", "hough.pyx"),
            *glob.glob(
                os.path.join("modules", "ift", "include", "opendrop", "*.hpp"),
                recursive=True,
            ),
            *all_files_recursive(os.path.join("modules", "ift", "include")),
            *all_files_recursive(os.path.join("modules", "ML_model")),
        ],
        "": extra_objects,
    },
    include_package_data=True,
    zip_safe=False,
)
