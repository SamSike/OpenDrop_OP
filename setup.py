from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import os
import sys

# setup for hpp/cpp

# Absolute base directory (project root)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Module paths
IFT_DIR = os.path.join(BASE_DIR, "modules", "ift")
YOUNGLAPLACE_DIR = os.path.join(IFT_DIR, "younglaplace")
INCLUDE_DIR = os.path.join(IFT_DIR, "include")

# Dependencies paths
SUNDIALS_INCLUDE = os.path.join(BASE_DIR, "dependencies","windows", "sundials", "include")
SUNDIALS_LIB = os.path.join(BASE_DIR, "dependencies","windows", "sundials", "lib")
BOOST_INCLUDE = os.path.join(BASE_DIR, "dependencies","windows", "boost")


# Compiler settings
is_windows = sys.platform.startswith("win")
is_linux = sys.platform.startswith("linux")
is_macos = sys.platform == "darwin"
extra_objects = []
compile_args = []
if is_windows:
    SUNDIALS_INCLUDE = os.path.join(BASE_DIR, "dependencies","windows", "sundials", "include")
    SUNDIALS_LIB = os.path.join(BASE_DIR, "dependencies","windows", "sundials", "lib")
    BOOST_INCLUDE = os.path.join(BASE_DIR, "dependencies","windows", "boost")
    extra_objects = [
        os.path.join(SUNDIALS_LIB, "sundials_arkode_static.lib"),
        os.path.join(SUNDIALS_LIB, "sundials_nvecserial_static.lib"),
        os.path.join(SUNDIALS_LIB, "sundials_core_static.lib"),
    ]
    compile_args = ["/std:c++17"]
    print("Windows detected, using Windows-specific settings.")
    print(f"SUNDIALS_INCLUDE: {SUNDIALS_INCLUDE}")
    print(f"SUNDIALS_LIB: {SUNDIALS_LIB}")
    print(f"BOOST_INCLUDE: {BOOST_INCLUDE}")
    print(f"extra_objects: {extra_objects}")
    print(f"compile_args: {compile_args}")
elif is_macos:
    SUNDIALS_INCLUDE = os.path.join(BASE_DIR, "dependencies", "macos", "sundials", "include")
    SUNDIALS_LIB = os.path.join(BASE_DIR, "dependencies", "macos", "sundials", "lib")
    BOOST_INCLUDE = os.path.join(BASE_DIR, "dependencies", "macos", "boost")
    extra_objects = [
        os.path.join(SUNDIALS_LIB, "libsundials_arkode.a"),
        os.path.join(SUNDIALS_LIB, "libsundials_nvecserial.a"),
        os.path.join(SUNDIALS_LIB, "libsundials_core.a"),
    ]
    compile_args = ["-std=c++17"]
    print("macOS detected, using macOS-specific settings.")
    print(f"SUNDIALS_INCLUDE: {SUNDIALS_INCLUDE}")
    print(f"SUNDIALS_LIB: {SUNDIALS_LIB}")
    print(f"BOOST_INCLUDE: {BOOST_INCLUDE}")
    print(f"extra_objects: {extra_objects}")
    print(f"compile_args: {compile_args}")
else:
    SUNDIALS_INCLUDE = os.path.join(BASE_DIR, "dependencies","linux", "sundials", "include")
    SUNDIALS_LIB = os.path.join(BASE_DIR, "dependencies","linux", "sundials", "lib")
    BOOST_INCLUDE = os.path.join(BASE_DIR, "dependencies","linux", "boost")
    
    extra_objects = [
        os.path.join(SUNDIALS_LIB, "libsundials_arkode.a"),
        os.path.join(SUNDIALS_LIB, "libsundials_nvecserial.a"),
        os.path.join(SUNDIALS_LIB, "libsundials_core.a"),
    ]
    compile_args = ["-std=c++17"]
    print("Linux detected, using Linux-specific settings.")
    print(f"SUNDIALS_INCLUDE: {SUNDIALS_INCLUDE}")
    print(f"SUNDIALS_LIB: {SUNDIALS_LIB}")
    print(f"BOOST_INCLUDE: {BOOST_INCLUDE}")
    print(f"extra_objects: {extra_objects}")
    print(f"compile_args: {compile_args}")

# Cython extension definitions
ext_modules = [
    Extension(
        name="ift.younglaplace.shape",
        sources=[os.path.join(YOUNGLAPLACE_DIR, "shape.pyx")],
        language="c++",
        include_dirs=[
            YOUNGLAPLACE_DIR,
            INCLUDE_DIR,
            SUNDIALS_INCLUDE,
            BOOST_INCLUDE
        ],
        extra_objects = extra_objects,
        extra_compile_args=compile_args,
        define_macros=[("SUNDIALS_STATIC", 1)],
    ),
    Extension(
        name="ift.hough.hough",
        sources=[os.path.join(IFT_DIR, "hough", "hough.pyx")],
        language="c++",
        include_dirs=[os.path.join(IFT_DIR, "hough")],
        extra_compile_args=compile_args,
    )
]

setup(
    name="OpenDrop_IFTExtensions",
    version="0.1.0",
    packages=find_packages(where="modules"),
    package_dir={"": "modules"},
    ext_modules=cythonize(
        ext_modules,
        compiler_directives={"language_level": "3"},
        include_path=[os.path.join(BASE_DIR, "modules")]
    ),
    zip_safe=False
)
