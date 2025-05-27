#ifndef CREATE_XGRID_GPU_WRAPPER_
#define CREATE_XGRID_GPU_WRAPPER_

int create_xgrid_order1_gpu_wrapper(int nx_src, int ny_src, int nx_dst, int ny_dst, double *x_src,
                                    double *y_src,  double *x_dst,  double *y_dst,
                                    double *mask_src, int *xgrid_ij1, int *xgrid_ij2, double *xgrid_area);

void create_xgrid_transfer_data(long int nxgrid, *xgrid_ij1_in, int *xgrid_ij2_in, double *xgrid_area_in);

#endif
