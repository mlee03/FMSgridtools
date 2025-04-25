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
#include "mosaic_util.h"
#include "interp_gpu.h"
#include "interp.h"
#include "create_xgrid.h"
#include "create_xgrid_gpu.h"
#include "create_xgrid_utils_gpu.h"

/*------------------------------------------------------------------------------
  void conserve_interp()
  conservative interpolation through exchange grid.
  Currently only first order interpolation are implemented here.
  ----------------------------------------------------------------------------*/
void conserve_interp_gpu(int nx_src, int ny_src, int nx_dst, int ny_dst, double *x_src,
                         double *y_src,  double *x_dst,  double *y_dst,
                         double *mask_src,  double *data_src, double *data_dst )
{
  Grid_cells_struct_config output_grid_cells;
  Interp_per_input_tile interp_gpu;

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

  int *xgrid_ij1 = interp_gpu.input_parent_cell_index;
  int *xgrid_ij2 = interp_gpu.output_parent_cell_index;
  double *xgrid_area = interp_gpu.xcell_area;
  double *dst_area; dst_area = (double *)malloc(nx_dst*ny_dst*sizeof(double));

  for(int n=0; n<nx_dst*ny_dst; n++) {
    dst_area[n] = 0.0;
    data_dst[n] = 0.0;
  }

  /* The source grid may not cover the destination grid
     so need to sum of exchange grid area to get dst_area
     get_grid_area(&nx_dst, &ny_dst, x_dst, y_dst, dst_area);
  */

  for(int n=0; n<nxgrid; n++) dst_area[xgrid_ij2[n]] += xgrid_area[n];
  for(int n=0; n<nxgrid; n++) {
    int ij2 = xgrid_ij2[n];
    int ij1 = xgrid_ij1[n];
    double area_frac = xgrid_area[n]/dst_area[ij2];
    data_dst[ij2] += data_src[ij1]*area_frac;
  }

  free(xgrid_ij1);
  free(xgrid_ij2);
  free(xgrid_area);
  free(approx_nxcells);
  free(ij2_start);
  free(ij2_end);

}; /* conserve_interp */
