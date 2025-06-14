# Generated by CMake

if("${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION}" LESS 2.8)
   message(FATAL_ERROR "CMake >= 2.8.12 required")
endif()
if(CMAKE_VERSION VERSION_LESS "2.8.12")
   message(FATAL_ERROR "CMake >= 2.8.12 required")
endif()
cmake_policy(PUSH)
cmake_policy(VERSION 2.8.12...3.30)
#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Protect against multiple inclusion, which would fail when already imported targets are added once more.
set(_cmake_targets_defined "")
set(_cmake_targets_not_defined "")
set(_cmake_expected_targets "")
foreach(_cmake_expected_target IN ITEMS SUNDIALS::core_static SUNDIALS::nvecserial_static SUNDIALS::nvecmanyvector_static SUNDIALS::sunmatrixband_static SUNDIALS::sunmatrixdense_static SUNDIALS::sunmatrixsparse_static SUNDIALS::sunlinsolband_static SUNDIALS::sunlinsoldense_static SUNDIALS::sunlinsolpcg_static SUNDIALS::sunlinsolspbcgs_static SUNDIALS::sunlinsolspfgmr_static SUNDIALS::sunlinsolspgmr_static SUNDIALS::sunlinsolsptfqmr_static SUNDIALS::sunnonlinsolnewton_static SUNDIALS::sunnonlinsolfixedpoint_static SUNDIALS::arkode_static SUNDIALS::cvode_static SUNDIALS::cvodes_static SUNDIALS::ida_static SUNDIALS::idas_static SUNDIALS::kinsol_static)
  list(APPEND _cmake_expected_targets "${_cmake_expected_target}")
  if(TARGET "${_cmake_expected_target}")
    list(APPEND _cmake_targets_defined "${_cmake_expected_target}")
  else()
    list(APPEND _cmake_targets_not_defined "${_cmake_expected_target}")
  endif()
endforeach()
unset(_cmake_expected_target)
if(_cmake_targets_defined STREQUAL _cmake_expected_targets)
  unset(_cmake_targets_defined)
  unset(_cmake_targets_not_defined)
  unset(_cmake_expected_targets)
  unset(CMAKE_IMPORT_FILE_VERSION)
  cmake_policy(POP)
  return()
endif()
if(NOT _cmake_targets_defined STREQUAL "")
  string(REPLACE ";" ", " _cmake_targets_defined_text "${_cmake_targets_defined}")
  string(REPLACE ";" ", " _cmake_targets_not_defined_text "${_cmake_targets_not_defined}")
  message(FATAL_ERROR "Some (but not all) targets in this export set were already defined.\nTargets Defined: ${_cmake_targets_defined_text}\nTargets not yet defined: ${_cmake_targets_not_defined_text}\n")
endif()
unset(_cmake_targets_defined)
unset(_cmake_targets_not_defined)
unset(_cmake_expected_targets)


# Compute the installation prefix relative to this file.
get_filename_component(_IMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" PATH)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)
if(_IMPORT_PREFIX STREQUAL "/")
  set(_IMPORT_PREFIX "")
endif()

# Create imported target SUNDIALS::core_static
add_library(SUNDIALS::core_static STATIC IMPORTED)

set_target_properties(SUNDIALS::core_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>"
)

# Create imported target SUNDIALS::nvecserial_static
add_library(SUNDIALS::nvecserial_static STATIC IMPORTED)

set_target_properties(SUNDIALS::nvecserial_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static"
)

# Create imported target SUNDIALS::nvecmanyvector_static
add_library(SUNDIALS::nvecmanyvector_static STATIC IMPORTED)

set_target_properties(SUNDIALS::nvecmanyvector_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static"
)

# Create imported target SUNDIALS::sunmatrixband_static
add_library(SUNDIALS::sunmatrixband_static STATIC IMPORTED)

set_target_properties(SUNDIALS::sunmatrixband_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static"
)

# Create imported target SUNDIALS::sunmatrixdense_static
add_library(SUNDIALS::sunmatrixdense_static STATIC IMPORTED)

set_target_properties(SUNDIALS::sunmatrixdense_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static"
)

# Create imported target SUNDIALS::sunmatrixsparse_static
add_library(SUNDIALS::sunmatrixsparse_static STATIC IMPORTED)

set_target_properties(SUNDIALS::sunmatrixsparse_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static"
)

# Create imported target SUNDIALS::sunlinsolband_static
add_library(SUNDIALS::sunlinsolband_static STATIC IMPORTED)

set_target_properties(SUNDIALS::sunlinsolband_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static;SUNDIALS::sunmatrixband_static"
)

# Create imported target SUNDIALS::sunlinsoldense_static
add_library(SUNDIALS::sunlinsoldense_static STATIC IMPORTED)

set_target_properties(SUNDIALS::sunlinsoldense_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static;SUNDIALS::sunmatrixdense_static"
)

# Create imported target SUNDIALS::sunlinsolpcg_static
add_library(SUNDIALS::sunlinsolpcg_static STATIC IMPORTED)

set_target_properties(SUNDIALS::sunlinsolpcg_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static"
)

# Create imported target SUNDIALS::sunlinsolspbcgs_static
add_library(SUNDIALS::sunlinsolspbcgs_static STATIC IMPORTED)

set_target_properties(SUNDIALS::sunlinsolspbcgs_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static"
)

# Create imported target SUNDIALS::sunlinsolspfgmr_static
add_library(SUNDIALS::sunlinsolspfgmr_static STATIC IMPORTED)

set_target_properties(SUNDIALS::sunlinsolspfgmr_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static"
)

# Create imported target SUNDIALS::sunlinsolspgmr_static
add_library(SUNDIALS::sunlinsolspgmr_static STATIC IMPORTED)

set_target_properties(SUNDIALS::sunlinsolspgmr_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static"
)

# Create imported target SUNDIALS::sunlinsolsptfqmr_static
add_library(SUNDIALS::sunlinsolsptfqmr_static STATIC IMPORTED)

set_target_properties(SUNDIALS::sunlinsolsptfqmr_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static"
)

# Create imported target SUNDIALS::sunnonlinsolnewton_static
add_library(SUNDIALS::sunnonlinsolnewton_static STATIC IMPORTED)

set_target_properties(SUNDIALS::sunnonlinsolnewton_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static"
)

# Create imported target SUNDIALS::sunnonlinsolfixedpoint_static
add_library(SUNDIALS::sunnonlinsolfixedpoint_static STATIC IMPORTED)

set_target_properties(SUNDIALS::sunnonlinsolfixedpoint_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static"
)

# Create imported target SUNDIALS::arkode_static
add_library(SUNDIALS::arkode_static STATIC IMPORTED)

set_target_properties(SUNDIALS::arkode_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static"
)

# Create imported target SUNDIALS::cvode_static
add_library(SUNDIALS::cvode_static STATIC IMPORTED)

set_target_properties(SUNDIALS::cvode_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static"
)

# Create imported target SUNDIALS::cvodes_static
add_library(SUNDIALS::cvodes_static STATIC IMPORTED)

set_target_properties(SUNDIALS::cvodes_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static"
)

# Create imported target SUNDIALS::ida_static
add_library(SUNDIALS::ida_static STATIC IMPORTED)

set_target_properties(SUNDIALS::ida_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static"
)

# Create imported target SUNDIALS::idas_static
add_library(SUNDIALS::idas_static STATIC IMPORTED)

set_target_properties(SUNDIALS::idas_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static"
)

# Create imported target SUNDIALS::kinsol_static
add_library(SUNDIALS::kinsol_static STATIC IMPORTED)

set_target_properties(SUNDIALS::kinsol_static PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "SUNDIALS_STATIC_DEFINE"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
  INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:-lm>;SUNDIALS::core_static"
)

# Load information for each installed configuration.
file(GLOB _cmake_config_files "${CMAKE_CURRENT_LIST_DIR}/SUNDIALSTargets-*.cmake")
foreach(_cmake_config_file IN LISTS _cmake_config_files)
  include("${_cmake_config_file}")
endforeach()
unset(_cmake_config_file)
unset(_cmake_config_files)

# Cleanup temporary variables.
set(_IMPORT_PREFIX)

# Loop over all imported files and verify that they actually exist
foreach(_cmake_target IN LISTS _cmake_import_check_targets)
  if(CMAKE_VERSION VERSION_LESS "3.28"
      OR NOT DEFINED _cmake_import_check_xcframework_for_${_cmake_target}
      OR NOT IS_DIRECTORY "${_cmake_import_check_xcframework_for_${_cmake_target}}")
    foreach(_cmake_file IN LISTS "_cmake_import_check_files_for_${_cmake_target}")
      if(NOT EXISTS "${_cmake_file}")
        message(FATAL_ERROR "The imported target \"${_cmake_target}\" references the file
   \"${_cmake_file}\"
but this file does not exist.  Possible reasons include:
* The file was deleted, renamed, or moved to another location.
* An install or uninstall procedure did not complete successfully.
* The installation package was faulty and contained
   \"${CMAKE_CURRENT_LIST_FILE}\"
but not all the files it references.
")
      endif()
    endforeach()
  endif()
  unset(_cmake_file)
  unset("_cmake_import_check_files_for_${_cmake_target}")
endforeach()
unset(_cmake_target)
unset(_cmake_import_check_targets)

# This file does not depend on other imported targets which have
# been exported from the same project but in a separate export set.

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
cmake_policy(POP)
