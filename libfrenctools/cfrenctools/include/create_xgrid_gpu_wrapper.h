#ifndef CREATE_XGRID_GPU_WRAPPER_
#define CREATE_XGRID_GPU_WRAPPER_

int create_xgrid_order1_gpu_wrapper(int nx_src, int ny_src, int nx_dst, int ny_dst, double *x_src,
                                    double *y_src,  double *x_dst,  double *y_dst,
                                    double *mask_src, double *mask_dst,
                                    int *xgrid_ij1, int *xgrid_ij2, double *xgrid_area);

void create_xgrid_transfer_data(int nxgrid, int src_nlon, int tgt_nlon,
                                int *src_i, int *src_j, int *tgt_i, int *tgt_j, double *xarea);

#endif
