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

set(INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/include)

# Create the shared library target
add_library(clib SHARED ${c_source_files})

target_include_directories(clib PUBLIC ${INCLUDE_DIR})

# Set the output directory
set_target_properties(
    clib PROPERTIES 
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/c_build
    POSITION_INDEPENDENT_CODE ON
    PREFIX ""
)

# Install the shared library
install(TARGETS clib DESTINATION c_build)