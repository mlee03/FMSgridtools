cmake_minimum_required(VERSION 3.10)
project(clib)

list(APPEND c_source_files
  make_hgrid/create_conformal_cubic_grid.c
  make_hgrid/create_gnomonic_cubic_grid.c
  make_hgrid/create_grid_from_file.c
  make_hgrid/create_lonlat_grid.c
  make_mosaic/get_contact.c
  make_topog/topog.c
  shared/create_xgrid.c
  shared/create_xgrid_gpu.c
  shared/create_xgrid_utils_gpu.c
  shared/general_utils_gpu.c
  shared/gradient_c2l.c
  shared/interp.c
  shared/interp_gpu.c
  shared/mosaic_util.c
  shared/mpp.c
  shared/mpp_domain.c
  shared/mpp_io.c
  shared/read_mosaic.c
  shared/tool_util.c
)

# use module in cmake folder to find netcdf
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)
find_package(MPI REQUIRED COMPONENTS C)
find_package(NetCDF REQUIRED COMPONENTS C)
find_package(OpenACC COMPONENTS C)

# macros that were previously set via autotools config.h
execute_process(
  COMMAND git rev-parse HEAD
  RESULT_VARIABLE GIT_RESULT
  OUTPUT_VARIABLE GIT_HASH
  ERROR_QUIET
)
add_definitions(-DGIT_HEADHASH="$GIT_HASH")
# TODO, should really get this from somewhere else instead of hardcoding
add_definitions(-DPACKAGE_VERSION="0.0.1")

set(SRC_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/include)

# Create the shared library target
add_library(clib SHARED ${c_source_files})

target_include_directories(clib PUBLIC 
    ${SRC_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/shared
    ${NetCDF_C_INCLUDE_DIRS}
)

target_link_libraries(clib PUBLIC NetCDF::NetCDF_C
                                  MPI::MPI_C
                                  OpenACC::OpenACC_C)


# Set the output directory
set_target_properties(
    clib PROPERTIES 
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/c_build
    POSITION_INDEPENDENT_CODE ON
    PREFIX ""
    COMPILE_FLAGS ${OpenACC_C_FLAGS}
)

# Install the shared library
install(TARGETS clib DESTINATION c_build)
