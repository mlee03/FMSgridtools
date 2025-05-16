/***********************************************************************
 *                   GNU Lesser General Public License
 *
 * This file is part of the GFDL FRE NetCDF tools package (FRE-NCTools).
 *
 * FRE-NCtools is free software: you can redistribute it and/or modify it under
 * the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or (at
 * your option) any later version.
 *
 * FRE-NCtools is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
 * for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with FRE-NCTools.  If not, see
 * <http://www.gnu.org/licenses/>.
 **********************************************************************/
/*
  Copyright (C) 2011 NOAA Geophysical Fluid Dynamics Lab, Princeton, NJ
*/
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <openacc.h>
#include "create_xgrid.h"
#include "create_xgrid_gpu.h"
#include "create_xgrid_utils_gpu.h"

Interp_per_input_tile interp_gpu;

int create_xgrid_order1_gpu_wrapper(int nx_src, int ny_src, int nx_dst, int ny_dst, double *x_src,
                                    double *y_src,  double *x_dst,  double *y_dst, double *mask_src)
{
  Grid_cells_struct_config output_grid_cells;

  int ncells_src = nx_src * ny_src;
  int ncells_dst = nx_dst * ny_dst;
  int ngridpts_src = (nx_src+1) * (ny_src+1);
  int ngridpts_dst = (nx_dst+1) * (ny_dst+1);
  int jstart = 0;
  int jend = ny_src-1;

  int *approx_nxcells; approx_nxcells = (int *)malloc(ncells_src*sizeof(int));
  int *ij2_start; ij2_start = (int *)malloc(ncells_src*sizeof(int));
  int *ij2_end; ij2_end = (int *)malloc(ncells_src*sizeof(int));

#pragma acc enter data copyin(x_src[:ngridpts_src], y_src[:ngridpts_src], \
                              x_dst[:ngridpts_dst], y_dst[:ngridpts_dst],\
                              mask_src[:ncells_src])

  get_grid_cell_struct_gpu(nx_dst, ny_dst, x_dst, y_dst, &output_grid_cells);

#pragma acc enter data create(approx_nxcells[:ncells_src], ij2_start[:ncells_src], ij2_end[:ncells_src])

  int upbound_nxcells = get_upbound_nxcells_2dx2d_gpu(nx_src, ny_src, nx_dst, ny_dst, jstart, jend,
                                                      x_src, y_src, x_dst, y_dst, mask_src, &output_grid_cells,
                                                      approx_nxcells, ij2_start, ij2_end);

  int nxgrid = create_xgrid_2dx2d_order1_gpu(nx_src, ny_src, nx_dst, ny_dst, jstart, jend, x_src, y_src,
                                             x_dst, y_dst, upbound_nxcells, mask_src, &output_grid_cells,
                                             approx_nxcells, ij2_start, ij2_end, &interp_gpu);

#pragma acc exit data copyout(interp_gpu.input_parent_cell_index[:nxgrid],  \
                              interp_gpu.output_parent_cell_index[:nxgrid], \
                              interp_gpu.xcell_area[:nxgrid])

  //deallocate output_grid_cells
  return nxgrid;

}

void create_xgrid_transfer_data(int nxgrid, int *xgrid_ij1_in, int *xgrid_ij2_in, double *xgrid_area_in)
{

  for(int ix=0; ix<nxgrid; ix++){
    xgrid_ij1_in[ix] = interp_gpu.input_parent_cell_index[ix];
    xgrid_ij2_in[ix] = interp_gpu.output_parent_cell_index[ix];
    xgrid_area_in[ix] = interp_gpu.xcell_area[ix];
  }

  free(interp_gpu.input_parent_cell_index);
  free(interp_gpu.output_parent_cell_index);
  free(interp_gpu.xcell_area);

}
