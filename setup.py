from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import os
import sys
import platform



# Compiler settings
is_windows = sys.platform.startswith("win")
is_linux = sys.platform.startswith("linux")
is_macos = sys.platform == "darwin"

if is_windows:
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Platform-specific folder: 'windows', 'linux', or 'darwin'
    PLATFORM_NAME = platform.system().lower()
    DEPENDENCIES_DIR = os.path.join(BASE_DIR, "dependencies", "windows")

    # Module directories
    IFT_DIR = os.path.join(BASE_DIR, "modules", "ift")
    YOUNGLAPLACE_DIR = os.path.join(IFT_DIR, "younglaplace")
    HOUGH_DIR = os.path.join(IFT_DIR, "hough")
    INCLUDE_DIR = os.path.join(IFT_DIR, "include")
    SUNDIALS_INCLUDE = os.path.join(DEPENDENCIES_DIR, "sundials", "include")
    SUNDIALS_LIB = os.path.join(DEPENDENCIES_DIR, "sundials", "lib")
    BOOST_INCLUDE = os.path.join(DEPENDENCIES_DIR, "boost")
    extra_objects = [
        os.path.join(SUNDIALS_LIB, "sundials_arkode_static.lib"),
        os.path.join(SUNDIALS_LIB, "sundials_nvecserial_static.lib"),
        os.path.join(SUNDIALS_LIB, "sundials_core_static.lib"),
    ]
    compile_args = ["/std:c++17"]
else:
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Platform-specific folder: 'windows', 'linux', or 'darwin'
    PLATFORM_NAME = platform.system().lower()
    DEPENDENCIES_DIR = os.path.join(BASE_DIR, "dependencies", "linux")

    # Module directories
    IFT_DIR = os.path.join(BASE_DIR, "modules", "ift")
    YOUNGLAPLACE_DIR = os.path.join(IFT_DIR, "younglaplace")
    HOUGH_DIR = os.path.join(IFT_DIR, "hough")
    INCLUDE_DIR = os.path.join(IFT_DIR, "include")
    SUNDIALS_INCLUDE = os.path.join(DEPENDENCIES_DIR, "sundials", "include")
    SUNDIALS_LIB = os.path.join(DEPENDENCIES_DIR, "sundials", "lib")
    BOOST_INCLUDE = os.path.join(DEPENDENCIES_DIR, "boost")
    
    extra_objects = [
        os.path.join(SUNDIALS_LIB, "libsundials_arkode.a"),
        os.path.join(SUNDIALS_LIB, "libsundials_nvecserial.a"),
        os.path.join(SUNDIALS_LIB, "libsundials_core.a"),
    ]
    compile_args = ["-std=c++17"]

# Extensions
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
        extra_objects=extra_objects,
        define_macros=[("SUNDIALS_STATIC", 1)],
        extra_compile_args=compile_args
    ),
    Extension(
        name="ift.hough.hough",
        sources=[os.path.join(HOUGH_DIR, "hough.pyx")],
        language="c++",
        include_dirs=[HOUGH_DIR],
        extra_compile_args=compile_args
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
        include_path=[IFT_DIR]
    ),
    zip_safe=False
)