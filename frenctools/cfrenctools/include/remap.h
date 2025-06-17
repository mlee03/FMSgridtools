#ifndef REMAP_H
#define REMAP_H

int check_nxcells();
int save_nxcells(int nxcells_in);
int save_src_ij(int *src_ij_in);
int save_tgt_ij(int *tgt_ij_in);
int save_xarea(double *xarea_in);
int get_src_ij(int *src_ij_in, bool free_mem);
int get_tgt_ij(int *src_ij_in, bool free_mem);                                                                                                                  int get_xarea(double *xarea_in, bool free_mem);
int free_src_ij();
int free_tgt_ij();
int free_xarea();

#endif
