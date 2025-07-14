#include <stdio.h>
#include <stdlib.h>
#include "create_xgrid_utils_gpu.h"
#include "create_xgrid_gpu.h"
#include "globals.h"

typedef struct component {
  int itile;
  int nx;
  int ny;
  double *x;
  double *y;
  double *mask;
  double *area;
} component;

int initialize_upbound_arrays(int n, int *approx_nxcells, int *ij2_start, int *ij2_end)
{  

#pragma acc parallel loop present(approx_nxcells[:n], ij2_start[:n], ij2_end[:n])
  for(int i=0; i<n; i++)
  {
    approx_nxcells[i] = 0;
    ij2_start[i] = 0;
    ij2_end[i] = 0;
  }
  return EXIT_SUCCESS;
}


//main function
int make_coupler_mosaic(int ntile_atm, int ntile_lnd, int ntile_ocn, int ocn_extended_south, 
                        component *atm, component *lnd, component *ocn, Interp_per_input_tile *atmxlnd,
                        Interp_per_input_tile *atmxocn)
{

  /*
  Interp_per_input_tile *atmxlnd;
  Interp_per_input_tile *atmxocn;
  atmxlnd = (Interp_per_input_tile *)malloc(ntile_lnd*sizeof(Interp_per_input_tile));
  atmxocn = (Interp_per_input_tile *)malloc(ntile_ocn*sizeof(Interp_per_input_tile));
  */

  for(int itile_atm=0; itile_atm<ntile_atm; itile_atm++) {

    component *iatm = atm+itile_atm;

    int nxa = iatm->nx;
    int nya = iatm->ny; 
    int na = nxa * nya;
    int na_p = (nxa+1)*(nya+1);

    int *approx_nxcells = NULL; approx_nxcells = (int *)malloc(na*sizeof(int));
    int *ij2_start = NULL;  ij2_start = (int *)malloc(na*sizeof(int));  
    int *ij2_end = NULL; ij2_end = (int *)malloc(na*sizeof(int));
 
    double *iatm_x = iatm->x;
    double *iatm_y = iatm->y;
    double *iatm_mask = iatm->mask;
#pragma acc enter data create(approx_nxcells[:na], ij2_start[:na], ij2_end[:na])
#pragma acc ender data copyin(iatm_x[:na_p], iatm_y[:na_p], iatm_mask[:na])

    //land
    for(int itile_lnd=0; itile_lnd<ntile_lnd; itile_lnd++) {
      
      component *ilnd = lnd+itile_lnd;
      Grid_cells_struct_config lnd_gridcells;

      int nxl = ilnd->nx;
      int nyl = ilnd->ny;
      int nl = nxl * nyl;
      int nl_p = (nxl+1)*(nyl+1);

      //zero arrays
      initialize_upbound_arrays(na, approx_nxcells, ij2_start, ij2_end);
            
      double *ilnd_x = ilnd->x;
      double *ilnd_y = ilnd->y;
      double *ilnd_mask = ilnd->mask;
#pragma acc enter data copyin(ilnd_x[:nl_p], ilnd_y[:nl_p], ilnd_mask[:nl])

      //get output_grid_cells
      get_grid_cell_struct_gpu(nxl, nyl, ilnd->x, ilnd->y, &lnd_gridcells);
      
      int jstart = 0;
      int jend = 0;
      
      int upbound_nxcells = get_upbound_nxcells_2dx2d_gpu(nxa, nya, nxl, nyl, jstart, jend, 
                                                          iatm->x, iatm->y, ilnd->x, ilnd->y,
                                                          iatm->mask, ilnd->mask,
                                                          &lnd_gridcells, approx_nxcells,
                                                          ij2_start, ij2_end);

      int nxcells = create_xgrid_2dx2d_order1_gpu(nxa, nya, nxl, nyl, jstart, jend,
                                                  iatm->x, iatm->y , ilnd->x, ilnd->y,
                                                  upbound_nxcells, iatm->mask, ilnd->mask,
                                                  &lnd_gridcells, approx_nxcells, 
                                                  ij2_start, ij2_end, atmxlnd+itile_lnd);

      //free lnd_gridcells xz    
      free_grid_cell_struct_gpu(nl, &lnd_gridcells);

#pragma acc exit data copyout(ilnd_x[:nl_p], ilnd_y[:nl_p], ilnd_mask[:nl])
      
    }
    
    //ocn
    for(int itile_ocn=0; itile_ocn<ntile_ocn; itile_ocn++) {
      
      component *iocn = ocn+itile_ocn;
      Grid_cells_struct_config ocn_gridcells;

      int nxo = iocn->nx;
      int nyo = iocn->ny;
      int no = nxo * nyo;
      int no_p = (nxo+1)*(nyo+1);
      
      initialize_upbound_arrays(na, approx_nxcells, ij2_start, ij2_end);      
      
      double *iocn_x = iocn->x;
      double *iocn_y = iocn->y;
      double *iocn_mask = iocn->mask;
#pragma acc enter data copyin(iocn_x[:no_p], iocn_y[:no_p], iocn_mask[:no])
      
      //get output_grid_cells
      get_grid_cell_struct_gpu(nxo, nyo, iocn->x, iocn->y, &ocn_gridcells);
      
      int jstart = 0;
      int jend = 0;

      int upbound_nxcells = get_upbound_nxcells_2dx2d_gpu(nxa, nya, nxo, nyo, jstart, jend, 
                                                          iatm->x, iatm->y, iocn->x, iocn->y,
                                                          iatm->mask, iocn->mask,
                                                          &ocn_gridcells, approx_nxcells,
                                                          ij2_start, ij2_end);

      int nxcells = create_xgrid_2dx2d_order1_gpu(nxa, nya, nxo, nyo, jstart, jend,
                                                  iatm->x, iatm->y , iocn->x, iocn->y,
                                                  upbound_nxcells, iatm->mask, iocn->mask,
                                                  &ocn_gridcells, approx_nxcells,
                                                  ij2_start, ij2_end, atmxocn+itile_ocn);     

      printf("upbound_nxcells %d ncells %d\n", upbound_nxcells, nxcells);

      //free ocn_gridcells
      free_grid_cell_struct_gpu(no, &ocn_gridcells);

#pragma acc exit data delete(iocn_x[:no_p], iocn_y[:no_p], iocn_mask[:no])

    }

#pragma acc exit data delete(iatm_x[:na_p], iatm_y[:na_p], iatm_mask[:na])
#pragma acc exit data delete(approx_nxcells[:na], ij2_start[:na], ij2_end[:na])
    
    free(approx_nxcells);
    free(ij2_start);
    free(ij2_end);

  }
  
  return EXIT_SUCCESS;

}
