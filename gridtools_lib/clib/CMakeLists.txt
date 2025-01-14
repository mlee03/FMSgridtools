cmake_minimum_required(VERSION 3.10)
project(clib)

list(APPEND c_source_files
  make_hgrid/create_conformal_cubic_grid.c
  make_hgrid/create_gnomonic_cubic_grid.c
  make_hgrid/create_grid_from_file.c
  make_hgrid/create_lonlat_grid.c
  make_mosaic/get_contact.c
  make_topog/topog.c
)

# Create the shared library target
add_library(clib.so SHARED make_hgrid/create_conformal_cubic_grid.c)

# Set the output directory
set_target_properties(
    clib.so PROPERTIES 
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/c_build
    POSITION_INDEPENDENT_CODE ON
    PREFIX ""
)

# Install the shared library
install(TARGETS clib.so DESTINATION c_build)