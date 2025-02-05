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
  shared/mosaic_util.c
  shared/mpp.c
  shared/mpp_domain.c
  shared/mpp_io.c
  shared/read_mosaic.c
  shared/tool_util.c
)

list(APPEND header_files
  make_hgrid/create_hgrid.h
  make_mosaic/get_contact.h
  make_topog/topog.h
  shared/constant.h
  shred/create_xgrid.h
  shared/create_xgrid_gpu.h
  shared/create_xgrid_utils_gpu.h
  shared/general_utils_gpu.h
  shared/globals_gpu.h
  shared/globals.h
  shared/gradient_c2l.h
  shared/interp.h
  shared/mosaic_util.h
  shared/mpp.h
  shared/mpp_domain.h
  shared/mpp_io.h
  shared/parameters_gpu.h
  shared/read_mosaic.h
  shared/tool_util.h
)

execute_process(
  COMMAND nc-config --includedir
  OUTPUT_VARIABLE NetCDF_INCLUDE_DIR
)

# Create the shared library target
add_library(clib SHARED ${c_source_files})

target_include_directories(clib PUBLIC 
    shared
    ${NetCDF_INCLUDE_DIR}
)

# Set the output directory
set_target_properties(
    clib PROPERTIES 
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/c_build
    POSITION_INDEPENDENT_CODE ON
    PREFIX ""
)

# Install the shared library
install(TARGETS clib DESTINATION c_build)
