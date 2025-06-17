#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include "remap.h"

static int nxcells = 0;
static int *src_ij = NULL;
static int *tgt_ij = NULL;
static double *xarea = NULL;

int check_nxcells()
{
  if(nxcells == 0) {
    printf("must set nxcells first\n");
    exit(1);
  }
  return EXIT_SUCCESS;
}

int save_nxcells(int nxcells_in)
{
  nxcells = nxcells_in;
  return EXIT_SUCCESS;
}

int save_src_ij(int *src_ij_in)
{
  check_nxcells();
  src_ij = (int *)malloc(nxcells*sizeof(int));
  memcpy(src_ij, src_ij_in, nxcells*sizeof(int));
  return EXIT_SUCCESS;
}

int save_tgt_ij(int *tgt_ij_in)
{
  check_nxcells();
  tgt_ij = (int *)malloc(nxcells*sizeof(int));
  memcpy(tgt_ij, tgt_ij_in, nxcells*sizeof(int));
  return EXIT_SUCCESS;
}

int save_xarea(double *xarea_in)
{
  check_nxcells();
  xarea = (double *)malloc(nxcells*sizeof(double));
  memcpy(xarea, xarea_in, nxcells*sizeof(double));
  return EXIT_SUCCESS;
}

int get_src_ij(int *src_ij_in, bool free_mem)
{
  check_nxcells();
  if(src_ij == NULL) return EXIT_FAILURE;
  memcpy(src_ij_in, src_ij, nxcells*sizeof(int));
  if(free_mem) free_src_ij();  
}

int get_tgt_ij(int *tgt_ij_in, bool free_mem)
{
  check_nxcells();
  if(tgt_ij == NULL) return EXIT_FAILURE;
  memcpy(tgt_ij_in, tgt_ij, nxcells*sizeof(int));
  if(free_mem) free_tgt_ij();  
}

int get_xarea(double *xarea_in, bool free_mem)
{
  check_nxcells();
  if(xarea_in == NULL) return EXIT_FAILURE;
  memcpy(xarea_in, xarea, nxcells*sizeof(double));
  if(free_mem) free_xarea();  
}

int free_src_ij()
{
  free(src_ij);
  src_ij = NULL;
  return EXIT_SUCCESS;
}

int free_tgt_ij()
{
  free(tgt_ij);
  tgt_ij = NULL;
  return EXIT_SUCCESS;
}

int free_xarea()
{
  free(xarea);
  xarea = NULL;
  return EXIT_SUCCESS;
}
  




