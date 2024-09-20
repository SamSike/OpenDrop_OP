# MacOS 

The `opendrop` library requires a Python version 3.10 to ensure compatibility with this requirement.


* Using a third-party package manager [Homebrew website](https://brew.sh/).

## Update and install necessary packages
```bash
# mpich or openmpi 
brew install python@3.10 scons glib cairo pkg-config gtk+3 mpich cmake boost git wget
```

## Clone and Build the Sundials repository into the same directory as the OpenDrop_OP project

```bash
git clone https://github.com/LLNL/sundials.git
cd sundials
git checkout tags/v7.1.1
mkdir build
cd build
cmake ..
make
sudo make install
```

## Clone and Build OpenDrop
```bash
git clone https://github.com/jdber1/opendrop.git
```

## Ensure latest file included in OpenDrop
Replace the SConstruct and requirements.txt in the root folder of opendrop\
(The latest version is uploaded in Teams/Documents/General/Dev Environment Setup/Set up opendrop on Fedora)

## Create and activate a virtual environment to run OpenDrop
```bash

. venv3.10/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
scons bdist_wheel # if main_menu.ui issue arise
python3.10 -m opendrop
```


#### <span style="color:red"> Troubleshooting Dependency Issue may arise
If you encounter issue while running `python3.10 -m opendrop`
```bash
"include/opendrop/younglaplace.hpp:12:10: fatal error: 'boost/math/differentiation/python3.10 -m venv venv3.10autodiff.hpp' file not found
#include <boost/math/differentiation/autodiff.hpp>
         ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1 error generated."
```
You can resolve this issue by locating all .hpp files present in your Boost directory and ensuring that the path to Boost headers is correctly specified.

1. Find the Boost Header Files
- Use the following command to find all .hpp files within the Boost directory:
```bash
find /opt/homebrew -name  "*.hpp" | grep boost
```
2. Set the BOOST_INCLUDE_DIR Environment Variable

- Once you have identified the correct path to the Boost headers, set the BOOST_INCLUDE_DIR environment variable to this path. 

```bash
export BOOST_INCLUDE_DIR=/opt/homebrew/Cellar/boost/1.86.0/include/
```
3. Update the SCons Configuration
- Update your SCons script to use the correct path for Boost headers. Modify the boost_include_dir variable in your `SConstruct` or `SConscript` file to use the environment variable:

```bash
# SConstruct
***
# Use the environment variable for the Boost include directory or a default path
boost_include_dir = os.getenv('BOOST_INCLUDE_DIR', '/opt/homebrew/Cellar/boost/version/include')
env.Append(CPPPATH=[boost_include_dir])
***
```
- Ensure that the path /opt/homebrew/Cellar/boost/version/include matches the actual location where Boost headers are installed.

4. Clean Build Artifacts
- Before rebuilding, clean any existing build artifacts to ensure a fresh build:
```bash
scons --clean
```
5. Rebuild the Project
- After cleaning, build the project again using:
```bash
scons bdist_wheel
```
6. Restart
- By following these steps, you should be able to resolve the missing file issue related to Boost in your project and rebuild it successfully.
```bash
python3.10 -m opendrop
```
