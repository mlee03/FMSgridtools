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
#ifndef INTERP_GPU_H_
#define INTERP_GPU_H_
/*********************************************************************
                     interp.h
   This header files contains defition of some interpolation routine  (1-D or 2-D).
   contact: Zhi.Liang@noaa.gov
*********************************************************************/
void conserve_interp_gpu(int nx_src, int ny_src, int nx_dst, int ny_dst, double *x_src,
                         double *y_src,  double *x_dst,  double *y_dst,
                         double *mask_src,  double *data_src, double *data_dst );
#endif
